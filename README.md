# Tesseract.js 日本語カスタムOCRシステム

tesseract.jsで独自のモデルを使った日本語OCRシステムです。独自にトレーニングしたモデルを使用して、より高精度な日本語文字認識を実現できます。

## プロジェクト構造

```
train-tesseract-jp/
├── docker-compose.yml      # Docker Compose設定（app + train）
├── app/                    # Webアプリケーション（OCR実行環境）
│   ├── Dockerfile         # アプリ用Dockerファイル
│   ├── index.html         # メインHTML
│   ├── main.js            # OCRロジック
│   ├── style.css          # スタイル
│   ├── package.json       # 依存関係
│   └── public/
│       └── tessdata/      # カスタムモデル配置場所（train/outputから自動マウント）
│
└── train/                  # モデルトレーニング環境
    ├── Dockerfile         # Tesseract環境
    ├── scripts/           # トレーニングスクリプト
    ├── source/            # トレーニング用テキストデータ
    ├── data/              # 生成されたトレーニングデータ
    ├── fonts/             # カスタムフォント
    └── output/            # トレーニング済みモデル（appと共有）
```

## 機能

### OCRアプリケーション（app）
- Webブラウザで動作する日本語OCR
- 画像ファイルのドラッグ&ドロップ対応
- 複数のモデルを選択可能
  - 標準日本語モデル（jpn）
  - カスタムモデル（jpn_custom）
  - 数字専用モデル（jpn - 数字のみ）
- **モデル切り替え時の自動事前ロード** - モデル選択時にバックグラウンドで読み込み
- **画像を表示したまま再実行** - モデルを切り替えて同じ画像で再度OCR可能
- リアルタイムで進捗表示
- 認識結果のコピー・ダウンロード機能

### trainフォルダ（モデルトレーニング）
- Dockerベースのトレーニング環境
- 日本語フォントからトレーニングデータを自動生成
- Tesseract LSTMモデルのファインチューニング
- カスタムフォント対応

## クイックスタート

### 1. アプリケーションの起動

```bash
# リポジトリのルートディレクトリで実行
docker compose up -d

# ブラウザで http://localhost:3333 を開く
```

これだけで、OCRアプリケーションがすぐに使えます！標準の日本語モデル（jpn）が自動で読み込まれます。

### 2. カスタムモデルのトレーニング（オプション）

より高精度な認識が必要な場合、カスタムモデルを作成できます：

```bash
bash train/retrain.sh
```

トレーニングには30分〜2時間程度かかります。完了後、ブラウザで「カスタムモデル (jpn_custom)」を選択して試せます。

## 使い方

### OCRアプリケーションの使い方

1. ブラウザで `http://localhost:3333` を開く
2. **モデルを選択**（標準 or カスタム）
   - モデル選択時、バックグラウンドで自動的に読み込みが開始されます
3. **画像をアップロード**またはドラッグ&ドロップ
4. **「OCR実行」ボタンをクリック**
   - 事前にモデルが読み込まれていれば、すぐにOCR処理が開始されます
5. **認識結果が表示される**
6. （オプション）**別のモデルで再実行**
   - 「別のモデルで再実行」ボタンをクリック
   - モデルを変更して、同じ画像で再度OCRを実行できます
   - 画像は表示されたままなので、モデルの精度を簡単に比較できます

### 新機能の詳細

#### モデル切り替え時の自動事前ロード
- モデルを選択した瞬間にバックグラウンドで読み込み開始
- OCR実行ボタンを押した時の待ち時間を大幅短縮
- ページ読み込み時にもデフォルトモデルを事前ロード

#### 画像を表示したまま再実行
- OCR実行後も画像が表示され続けるため、モデルを切り替えて再度実行可能
- 複数のモデルの認識精度を簡単に比較できます

### カスタムモデルのトレーニング（詳細）

基本的には `bash train/retrain.sh` だけで完了します。このスクリプトが以下を自動実行します：

1. トレーニングデータの生成（`scripts/generate_training_data.py`）
2. モデルのトレーニング（`scripts/train_model.sh`）
3. 生成されたモデルを自動配置（`train/output/jpn_custom.traineddata`）

## 要件

- Docker Desktop または Docker + Docker Compose
- 推奨：8GB以上のRAM（トレーニング実行時）
- モダンWebブラウザ（Chrome、Firefox、Safari、Edgeなど）

## カスタマイズ

### トレーニングデータのカスタマイズ

特定のドメイン（例：請求書、領収書など）に特化したモデルを作成する場合：

1. **トレーニングテキストを編集**
   - `train/source/training_texts.txt` を編集
   - 会社名、住所、電話番号など、認識したいテキストを追加
   - データ拡張は `expand_training_texts.py` が自動で行います

2. **独自のフォントを追加**（オプション）
   - `.ttf` または `.otf` フォントを `train/fonts/` に配置
   - トレーニング時に自動的に使用されます

3. **トレーニングを実行**
   ```bash
   bash train/retrain.sh
   ```

### UIのカスタマイズ

`app/style.css` と `app/index.html` を編集してUIを変更できます。

## トラブルシューティング

### カスタムモデルが読み込めない

1. `train/output/jpn_custom.traineddata.gz` が存在するか確認
2. アプリコンテナを再起動: `docker compose restart app`
3. ブラウザのキャッシュをクリア（Ctrl+Shift+Delete / Cmd+Shift+Delete）
4. ブラウザの開発者ツール（F12）でコンソールエラーを確認

### トレーニングが失敗する

1. Docker Desktopのメモリ設定を確認（推奨：8GB以上）
2. `train/data/` にトレーニング画像（.tifファイル）が生成されているか確認
3. `docker compose logs train` でログを確認

### OCRの精度を上げたい

1. `train/source/training_texts.txt` に認識したいテキストを追加
2. トレーニング回数を増やす（`train/scripts/train_model.sh`の`--max_iterations`を変更）
3. `bash train/retrain.sh` で再トレーニング

## ライセンス

このプロジェクトはMITライセンスです。

## 技術スタック

### app
- [Tesseract.js](https://tesseract.projectnaptha.com/) - JavaScript OCRライブラリ
- [Vite](https://vitejs.dev/) - ビルドツール
- Vanilla JavaScript

### train
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCRエンジン
- [tesstrain](https://github.com/tesseract-ocr/tesstrain) - トレーニングツール
- Python 3
- Docker

## 参考リンク

- [Tesseract.js Documentation](https://tesseract.projectnaptha.com/)
- [Tesseract OCR Documentation](https://tesseract-ocr.github.io/)
- [Train Your Tesseract](https://tesseract-ocr.github.io/tessdoc/Training-Tesseract.html)

## コントリビューション

プルリクエスト、Issue報告は大歓迎です。

## サポート

質問やバグ報告は、GitHubのIssuesでお願いします。
