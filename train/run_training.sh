#!/bin/bash
# ワンコマンドでトレーニングを実行するスクリプト（最新版）
# 使用スクリプト：
#   - expand_training_texts.py: テキストデータの拡張（オプション）
#   - generate_training_data.py: text2imageでトレーニング画像生成
#   - train_model.sh: LSTMモデルのトレーニング

set -e

echo "============================================"
echo "Tesseract 日本語カスタムモデル トレーニング"
echo "============================================"
echo ""

# カレントディレクトリの確認
if [ ! -f "../docker-compose.yml" ]; then
    echo "エラー: このスクリプトはtrainディレクトリから実行してください"
    exit 1
fi

# Dockerの確認
if ! command -v docker &> /dev/null; then
    echo "エラー: Dockerがインストールされていません"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "エラー: Docker Composeがインストールされていません"
    exit 1
fi

echo "ステップ 1/6: Docker環境のビルド"
echo "----------------------------------------"
docker compose -f ../docker-compose.yml build train

echo ""
echo "ステップ 2/6: コンテナの起動"
echo "----------------------------------------"
docker compose -f ../docker-compose.yml up -d train

echo ""
echo "ステップ 3/6: トレーニングテキストの拡張（オプション）"
echo "----------------------------------------"
read -p "トレーニングテキストを拡張しますか？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose -f ../docker-compose.yml exec -T train python3 scripts/expand_training_texts.py
    echo "✓ テキストデータを拡張しました"
else
    echo "スキップしました（既存のtraining_texts_expanded.txtを使用）"
fi

echo ""
echo "ステップ 4/6: トレーニングデータの生成（text2image）"
echo "----------------------------------------"
echo "これには10〜20分かかる場合があります..."
# MAX_WORKERS環境変数でワーカー数を指定可能（デフォルト: CPU数×2）
docker compose -f ../docker-compose.yml exec -T train bash -c "PYTHONUNBUFFERED=1 MAX_WORKERS=${MAX_WORKERS:-12} python3 scripts/generate_training_data.py"

echo ""
echo "ステップ 5/6: モデルのトレーニング（LSTM）"
echo "----------------------------------------"
echo "これには30分〜1時間かかる場合があります..."
# PARALLEL_JOBS環境変数でlstmf生成の並列数を指定可能（デフォルト: 12）
docker compose -f ../docker-compose.yml exec -T train bash -c "PARALLEL_JOBS=${PARALLEL_JOBS:-12} bash scripts/train_model.sh"

echo ""
echo "ステップ 6/6: トレーニング済みモデルのコピー"
echo "----------------------------------------"
docker cp tesseract-train-jp:/workspace/output/jpn_custom.traineddata ./output/

# アプリフォルダが存在する場合は自動的にコピー
if [ -d "../app/public/tessdata" ]; then
    cp ./output/jpn_custom.traineddata ../app/public/tessdata/
    # gzip圧縮版も作成
    gzip -k -f ../app/public/tessdata/jpn_custom.traineddata
    echo "✓ モデルを app/public/tessdata/ にコピーしました"
    echo "✓ gzip圧縮版も作成しました"
else
    echo "注意: app/public/tessdata/ が見つかりません"
    echo "手動でコピーしてください: cp output/jpn_custom.traineddata ../app/public/tessdata/"
fi

echo ""
echo "============================================"
echo "トレーニング完了！"
echo "============================================"
echo ""
echo "出力ファイル:"
echo "  - train/output/jpn_custom.traineddata"
if [ -d "../app/public/tessdata" ]; then
    echo "  - app/public/tessdata/jpn_custom.traineddata"
    echo "  - app/public/tessdata/jpn_custom.traineddata.gz"
fi
echo ""
echo "生成されたファイル数:"
TIFF_COUNT=$(ls -1 ./data/*.tif 2>/dev/null | wc -l | tr -d ' ')
BOX_COUNT=$(ls -1 ./data/*.box 2>/dev/null | wc -l | tr -d ' ')
LSTMF_COUNT=$(ls -1 ./data/*.lstmf 2>/dev/null | wc -l | tr -d ' ')
echo "  - 画像ファイル(.tif): $TIFF_COUNT"
echo "  - BOXファイル(.box): $BOX_COUNT"
echo "  - LSTMファイル(.lstmf): $LSTMF_COUNT"
echo ""
echo "次のステップ:"
echo "1. cd ../app"
echo "2. npm run dev （既に起動している場合は不要）"
echo "3. ブラウザで http://localhost:3333 を開く"
echo "4. モデル選択で「カスタムモデル (jpn_custom)」を選択"
echo "5. テスト画像をアップロードして精度を確認"
echo ""
echo "コンテナを停止する場合:"
echo "  cd .. && docker compose down"
echo ""
