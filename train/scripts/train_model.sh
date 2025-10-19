#!/bin/bash
set -e

# 設定
MODEL_NAME="jpn_custom"
START_MODEL="jpn"
TESSDATA="/usr/local/share/tessdata"
WORK_DIR="/workspace"
DATA_DIR="$WORK_DIR/data"
OUTPUT_DIR="$WORK_DIR/output"

echo "===================================="
echo "Tesseract カスタムモデルトレーニング"
echo "===================================="

# ベースモデルのダウンロード（LSTM継続トレーニング用にtessdata_bestを使用）
echo "ベースモデルをダウンロード中..."
if [ ! -f "$TESSDATA/${START_MODEL}.traineddata" ]; then
    echo "tessdata_bestからダウンロード（継続トレーニング用）..."
    wget -P $TESSDATA https://github.com/tesseract-ocr/tessdata_best/raw/main/${START_MODEL}.traineddata
else
    # 既存ファイルがtessdata_fastの可能性があるのでチェック
    FILE_SIZE=$(stat -f%z "$TESSDATA/${START_MODEL}.traineddata" 2>/dev/null || stat -c%s "$TESSDATA/${START_MODEL}.traineddata")
    if [ "$FILE_SIZE" -lt 10000000 ]; then
        echo "既存ファイルがtessdata_fastです。tessdata_bestに置き換えます..."
        rm -f "$TESSDATA/${START_MODEL}.traineddata"
        wget -P $TESSDATA https://github.com/tesseract-ocr/tessdata_best/raw/main/${START_MODEL}.traineddata
    fi
fi

# 出力ディレクトリの作成
mkdir -p $OUTPUT_DIR
cd $OUTPUT_DIR

# トレーニングデータの確認
TIFF_COUNT=$(ls -1 $DATA_DIR/*.tif 2>/dev/null | wc -l)
echo "トレーニング画像数: $TIFF_COUNT"

if [ $TIFF_COUNT -eq 0 ]; then
    echo "エラー: トレーニング画像が見つかりません"
    echo "まず generate_training_data.py を実行してください"
    exit 1
fi

# BOXファイルの生成
echo "BOXファイルを生成中..."
for tif in $DATA_DIR/*.tif; do
    base=$(basename "$tif" .tif)
    if [ ! -f "$DATA_DIR/$base.box" ]; then
        tesseract "$tif" "$DATA_DIR/$base" -l $START_MODEL --psm 6 makebox
        echo "  生成: $base.box"
    fi
done

# lstmfファイルの生成（並列処理）
echo "LSTMファイルを生成中（並列処理）..."

# CPU数を取得（環境変数で上書き可能、デフォルト: 12）
PARALLEL_JOBS=${PARALLEL_JOBS:-12}

echo "並列ジョブ数: $PARALLEL_JOBS"

# lstmfファイルが存在しないtifファイルのリストを作成
find $DATA_DIR -name "*.tif" | while read tif; do
    base=$(basename "$tif" .tif)
    if [ ! -f "$DATA_DIR/$base.lstmf" ]; then
        echo "$tif"
    fi
done > /tmp/tif_files_to_process.txt

TOTAL_FILES=$(wc -l < /tmp/tif_files_to_process.txt | tr -d ' ')
echo "処理対象ファイル数: $TOTAL_FILES"

if [ $TOTAL_FILES -gt 0 ]; then
    # xargsで並列処理
    cat /tmp/tif_files_to_process.txt | xargs -P $PARALLEL_JOBS -I {} bash -c '
        tif="{}"
        base=$(basename "$tif" .tif)
        base_dir=$(dirname "$tif")
        tesseract "$tif" "$base_dir/$base" -l jpn --psm 6 lstm.train 2>&1 | grep -v "Tesseract Open Source"
    '
    echo "全てのLSTMファイル生成完了"
else
    echo "全てのLSTMファイルは既に存在します"
fi

# トレーニングリストファイルの作成
echo "トレーニングリストを作成中..."
ls -1 $DATA_DIR/*.lstmf > $OUTPUT_DIR/training_files.txt

# モデルトレーニング開始
echo "モデルのトレーニング開始..."

# traineddataからlstmを抽出
echo "LSTMモデルを抽出中..."
combine_tessdata -e $TESSDATA/${START_MODEL}.traineddata $OUTPUT_DIR/${START_MODEL}_extracted.lstm

# 既存モデルから継続学習
# ScrollViewを無効化（debug_interval -1で完全に無効化）
# イテレーション数を大幅に増やして精度向上（10,000 → 50,000）
lstmtraining \
    --model_output $OUTPUT_DIR/$MODEL_NAME \
    --continue_from $OUTPUT_DIR/${START_MODEL}_extracted.lstm \
    --traineddata $TESSDATA/${START_MODEL}.traineddata \
    --train_listfile $OUTPUT_DIR/training_files.txt \
    --max_iterations 50000 \
    --debug_interval -1 \
    --learning_rate 0.001

# 最終モデルの作成
echo "最終モデルを作成中..."
lstmtraining \
    --stop_training \
    --continue_from $OUTPUT_DIR/${MODEL_NAME}_checkpoint \
    --traineddata $TESSDATA/${START_MODEL}.traineddata \
    --model_output $OUTPUT_DIR/${MODEL_NAME}.traineddata

echo "===================================="
echo "トレーニング完了！"
echo "出力: $OUTPUT_DIR/${MODEL_NAME}.traineddata"
echo "===================================="
echo ""
echo "このファイルを app/public/tessdata/ にコピーして使用してください"
