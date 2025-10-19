#!/bin/bash
# トレーニングデータを最初から再生成するスクリプト

set -e

echo "============================================"
echo "トレーニングデータの再生成"
echo "============================================"
echo ""

# Dockerコンテナが起動しているか確認
if ! docker compose ps | grep -q "train.*running"; then
    echo "Dockerコンテナを起動中..."
    docker compose -f ../docker-compose.yml up -d train
    sleep 3
fi

echo "ステップ 1/4: 古いデータの削除"
echo "----------------------------------------"
docker compose -f ../docker-compose.yml exec -T train bash -c "
    rm -f /workspace/data/*.tif
    rm -f /workspace/data/*.box
    rm -f /workspace/data/*.lstmf
    echo '古いトレーニングデータを削除しました'
"

echo ""
echo "ステップ 2/4: トレーニングテキストの再拡張"
echo "----------------------------------------"
docker compose -f ../docker-compose.yml exec -T train python3 scripts/expand_training_texts.py

echo ""
echo "ステップ 3/4: トレーニングデータの生成（text2image）"
echo "----------------------------------------"
echo "これには10〜20分かかる場合があります..."
# MAX_WORKERS環境変数でワーカー数を指定可能（デフォルト: 12）
docker compose -f ../docker-compose.yml exec -T train bash -c "PYTHONUNBUFFERED=1 MAX_WORKERS=${MAX_WORKERS:-12} python3 scripts/generate_training_data.py"

echo ""
echo "ステップ 4/4: モデルのトレーニング（LSTM）"
echo "----------------------------------------"
echo "これには1〜2時間かかる場合があります..."
# PARALLEL_JOBS環境変数でlstmf生成の並列数を指定可能（デフォルト: 12）
docker compose -f ../docker-compose.yml exec -T train bash -c "PARALLEL_JOBS=${PARALLEL_JOBS:-12} bash scripts/train_model.sh"

echo ""
echo "完了: トレーニング済みモデルのコピー"
echo "----------------------------------------"
docker cp tesseract-train-jp:/workspace/output/jpn_custom.traineddata ./output/

# アプリフォルダが存在する場合は自動的にコピー
if [ -d "../app/public/tessdata" ]; then
    cp ./output/jpn_custom.traineddata ../app/public/tessdata/
    gzip -k -f ../app/public/tessdata/jpn_custom.traineddata
    echo "✓ モデルを app/public/tessdata/ にコピーしました"
    echo "✓ gzip圧縮版も作成しました"
fi

echo ""
echo "============================================"
echo "再トレーニング完了！"
echo "============================================"
echo ""
echo "生成されたファイル数:"
TIFF_COUNT=$(ls -1 ./data/*.tif 2>/dev/null | wc -l | tr -d ' ')
BOX_COUNT=$(ls -1 ./data/*.box 2>/dev/null | wc -l | tr -d ' ')
LSTMF_COUNT=$(ls -1 ./data/*.lstmf 2>/dev/null | wc -l | tr -d ' ')
echo "  - 画像ファイル(.tif): $TIFF_COUNT"
echo "  - BOXファイル(.box): $BOX_COUNT"
echo "  - LSTMファイル(.lstmf): $LSTMF_COUNT"
echo ""
echo "テスト: カスタムモデルで認識確認"
docker compose -f ../docker-compose.yml exec train bash -c "
    cp /workspace/output/jpn_custom.traineddata /usr/local/share/tessdata/ && \
    cd /workspace/data && \
    echo '--- 標準モデル (jpn) ---' && \
    tesseract jpn_custom.train_0000.tif stdout -l jpn --psm 6 && \
    echo '' && \
    echo '--- カスタムモデル (jpn_custom) ---' && \
    tesseract jpn_custom.train_0000.tif stdout -l jpn_custom --psm 6
"
