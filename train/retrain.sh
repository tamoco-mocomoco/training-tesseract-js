#!/bin/bash
# 再トレーニング用スクリプト（lstmfファイルを再生成してトレーニング）

set -e

echo "============================================"
echo "Tesseract カスタムモデル 再トレーニング"
echo "============================================"
echo ""

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Dockerコンテナが起動しているか確認
if ! docker compose -C "$PROJECT_ROOT" ps | grep -q "train.*running"; then
    echo "Dockerコンテナを起動中..."
    docker compose -C "$PROJECT_ROOT" up -d train
    sleep 3
fi

echo "ステップ 1/2: lstmfファイルの再生成とモデルトレーニング"
echo "----------------------------------------"
echo "これには1〜2時間かかる場合があります..."
# PARALLEL_JOBS環境変数でlstmf生成の並列数を指定可能（デフォルト: 12）
docker compose -C "$PROJECT_ROOT" exec -T train bash -c "PARALLEL_JOBS=${PARALLEL_JOBS:-12} bash scripts/train_model.sh"

echo ""
echo "ステップ 2/2: トレーニング済みモデルのコピー"
echo "----------------------------------------"
docker cp tesseract-train-jp:/workspace/output/jpn_custom.traineddata "$SCRIPT_DIR/output/"

# アプリフォルダが存在する場合は自動的にコピー
if [ -d "$PROJECT_ROOT/app/public/tessdata" ]; then
    cp "$SCRIPT_DIR/output/jpn_custom.traineddata" "$PROJECT_ROOT/app/public/tessdata/"
    # gzip圧縮版も作成
    gzip -k -f "$PROJECT_ROOT/app/public/tessdata/jpn_custom.traineddata"
    echo "✓ モデルを app/public/tessdata/ にコピーしました"
    echo "✓ gzip圧縮版も作成しました"
else
    echo "注意: app/public/tessdata/ が見つかりません"
fi

echo ""
echo "============================================"
echo "再トレーニング完了！"
echo "============================================"
echo ""
echo "テスト: カスタムモデルで認識確認"
docker compose -C "$PROJECT_ROOT" exec train bash -c "
    cp /workspace/output/jpn_custom.traineddata /usr/local/share/tessdata/ && \
    cd /workspace/data && \
    echo '標準モデル:' && \
    tesseract jpn_custom.train_0000.tif stdout -l jpn --psm 6 && \
    echo 'カスタムモデル:' && \
    tesseract jpn_custom.train_0000.tif stdout -l jpn_custom --psm 6
"

echo ""
echo "ブラウザで http://localhost:3333 を開いてカスタムモデルをテストしてください"
