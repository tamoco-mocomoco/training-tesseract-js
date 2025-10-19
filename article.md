---
title: "Tesseract.jsでカスタムモデルを使った日本語OCRアプリを作った"
emoji: "🔍"
type: "tech"
topics: ["tesseract", "ocr", "javascript", "docker", "machinelearning"]
published: false
---

## はじめに

ブラウザで動作するOCRライブラリ「Tesseract.js」を使って、日本語認識のアプリケーションを作ろうとしたところ、**自分でトレーニングしたカスタムモデルを使用する具体的な例が見つからない**という壁にぶつかりました。

公式ドキュメントには標準モデルの使い方は豊富にありますが、カスタムモデルのトレーニングから実際にブラウザで動かすまでの一連の流れを扱った例はほとんどなく、特に以下の点で困りました：

- Tesseract 5.x系でのLSTMモデルのトレーニング方法
- トレーニングしたモデル（.traineddata）をTesseract.jsで読み込む方法
- 開発環境とGitHub Pages両方で動作させる設定

そこで、**モデルのトレーニング環境とブラウザでの動作確認ページを統合した開発環境**を作ることにしました。

## 作ったもの

https://github.com/tamoco-mocomoco/training-tesseract-js

リポジトリには以下が含まれています：

1. **Webアプリケーション**（`app/`）
   - Tesseract.js v5を使った日本語OCR
   - 標準モデルとカスタムモデルの切り替え
   - モデルの事前ロード機能
   - 画像を表示したまま複数モデルで再実行可能

2. **モデルトレーニング環境**（`train/`）
   - Dockerベースの完全なトレーニング環境
   - 日本語フォントからトレーニングデータを自動生成
   - Tesseract LSTMモデルのファインチューニング

3. **GitHub Pagesデモ**
   https://tamoco-mocomoco.github.io/training-tesseract-js/

## 技術スタック

### フロントエンド（app）
- [Tesseract.js](https://tesseract.projectnaptha.com/) v5 - ブラウザで動くOCRライブラリ
- [Vite](https://vitejs.dev/) - 高速な開発サーバーとビルドツール
- Vanilla JavaScript - フレームワークなしのシンプル実装

### トレーニング環境（train）
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) 5.x - OCRエンジン本体
- Python 3 - トレーニングデータ生成スクリプト
- Docker / Docker Compose - 環境の再現性確保

## プロジェクト構成

```
train-tesseract-jp/
├── docker-compose.yml      # app + train の統合環境
├── app/                    # Webアプリケーション
│   ├── Dockerfile
│   ├── index.html
│   ├── main.js            # OCRロジック
│   ├── style.css
│   ├── vite.config.js     # GitHub Pages対応
│   └── public/
│       └── tessdata/      # カスタムモデル配置場所
│
└── train/                  # トレーニング環境
    ├── Dockerfile
    ├── retrain.sh         # ワンコマンドでトレーニング
    ├── scripts/           # トレーニングスクリプト
    ├── source/            # トレーニング用テキストデータ
    ├── fonts/             # カスタムフォント
    └── output/            # トレーニング済みモデル（appと共有）
```

## 標準モデルとカスタムモデルの比較

実際に運転免許証のサンプル画像でOCRを実行し、標準モデル（jpn）とカスタムモデル（jpn_custom）の認識結果を比較してみました。

### 標準モデル（jpn）の認識結果

```
(所 | 東京 都 千 代田 区 霞が関 2ー 1 ーー

[| 云 介 | 令 和 01 年 05 有 07 昌 12345

2 眼鏡 等 に ビー ヨ
見 本 昌 に

| 第 0U12345678900 号 固

[ ま 15 04』018 ほ 基 還 に に 内 剛 " 攻 革
7061 昌 ) 屋 な
08801 絡 骨 暴 本 | 2558s
```

### カスタムモデル（jpn_custom）の認識結果

```
(所 東京 都 千 代田 区 霞が関 2 ご 1 ー2

[1 4015053075 12345

32 上 5 き 会
見 本

# 引 第 012345678900 呈 剛

還 i5504801g 雇 婦 医 頭 "-
時 昌明 部 ) 匠
888881 能 還 遇 5
```

### 考察

精度自体の向上は限定的ですが、**モデルによって認識結果が明確に異なる**ことが確認できました。これは以下の点を示しています：

- カスタムモデルは独自のトレーニングデータで学習されている
- ドメイン特化のテキストでトレーニングすれば、特定用途での精度向上が期待できる
- モデル切り替え機能により、複数モデルでの結果比較が容易

今回は汎用的なトレーニングデータを使用しましたが、運転免許証や請求書など**特定のフォーマットに特化したテキスト**でトレーニングすることで、より高い精度を実現できる可能性があります。

## 実装のポイント

### 1. モデルの事前ロード機能

Tesseract.jsでは、OCR実行時にモデルのダウンロードと初期化が行われるため、初回実行時に数秒待つ必要があります。これを改善するため、**モデル選択時にバックグラウンドで事前ロード**する仕組みを実装しました。

```javascript:app/main.js
// 状態管理
let worker = null;
let isWorkerReady = false;
let isLoadingWorker = false;

// モデル選択時のWorker事前作成
modelSelect.addEventListener('change', async () => {
    const selectedModel = modelSelect.value;

    if (isLoadingWorker) return;

    isLoadingWorker = true;
    isWorkerReady = false;

    try {
        // 既存のWorkerがあれば終了
        if (worker) {
            await worker.terminate();
            worker = null;
        }

        console.log('[Tesseract] Pre-loading model:', selectedModel);
        worker = await createModelWorker(selectedModel);
        isWorkerReady = true;
    } catch (error) {
        console.error('[Tesseract] Failed to pre-load model:', error);
        worker = null;
        isWorkerReady = false;
    } finally {
        isLoadingWorker = false;
    }
});
```

これにより、ユーザーがモデルを選択した瞬間からバックグラウンドで読み込みが始まり、**OCR実行ボタンを押した時の待ち時間が大幅に短縮**されます。

### 2. カスタムモデルの読み込み

Tesseract.jsでカスタムモデルを使用する際は、`langPath`オプションで配置場所を指定します。ここで重要なのは、**開発環境とGitHub Pages両方で動作する相対パス**を使うことです。

```javascript:app/main.js
async function createModelWorker(modelName) {
    if (modelName === 'jpn_custom') {
        return await createWorker(modelName, 1, {
            langPath: './tessdata'  // 相対パスがポイント
        });
    } else {
        return await createWorker(modelName);
    }
}
```

Viteの`base`設定と組み合わせることで、パスが自動的に解決されます：

```javascript:app/vite.config.js
export default defineConfig({
  base: process.env.NODE_ENV === 'production'
    ? '/training-tesseract-js/'  // GitHub Pages用
    : '/',                         // 開発環境用
  // ...
});
```

- 開発環境: `http://localhost:3333/tessdata/jpn_custom.traineddata.gz`
- GitHub Pages: `https://tamoco-mocomoco.github.io/training-tesseract-js/tessdata/jpn_custom.traineddata.gz`

### 3. ホワイトリストを使った文字制限

カスタムモデルをトレーニングしなくても、**ホワイトリスト機能で認識する文字を制限**することで、特定用途に最適化できます。

例えば、数字だけを認識したい場合：

```javascript:app/main.js
async function createModelWorker(modelName) {
    // ... 省略 ...

    if (modelName === 'jpn_numbers') {
        // 数字専用モデル（標準engモデルをホワイトリストで制限）
        const worker = await createWorker('eng');
        await worker.setParameters({
            tessedit_char_whitelist: '0123456789'
        });
        return worker;
    }

    // ... 省略 ...
}
```

この方法のメリット：

- **トレーニング不要** - すぐに使える
- **高速** - 軽量な英語モデル（eng）をベースにできる
- **精度向上** - 認識対象を絞ることで誤認識が減る
- **柔軟** - 数字だけ、英数字のみ、カタカナのみなど、用途に応じて設定可能

他の用途例：

```javascript
// 英数字のみ
await worker.setParameters({
    tessedit_char_whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
});

// カタカナのみ（例）
await worker.setParameters({
    tessedit_char_whitelist: 'アイウエオカキクケコ...'  // 必要な文字を列挙
});
```

特に請求書の金額欄や、フォームの番号フィールドなど、**認識する文字種が明確な場合に有効**です。

### 4. 画像を表示したまま再実行

複数のモデルで精度を比較したい場合、毎回画像をアップロードし直すのは面倒です。そこで、**OCR実行後も画像を表示したまま、モデルを切り替えて再実行できる**機能を実装しました。

```javascript:app/main.js
// OCR実行後も画像は表示したまま
async function performOCR(image) {
    try {
        // ... OCR処理 ...

        // 結果表示（画像は非表示にしない）
        setTimeout(() => {
            displayResult(text, confidence, processingTime);
        }, 500);

    } catch (error) {
        // エラー処理
    }
}

// 再実行ボタン
rerunBtn.addEventListener('click', () => {
    // 結果セクションを非表示にしてプレビューセクションにスクロール
    resultSection.style.display = 'none';
    previewSection.scrollIntoView({ behavior: 'smooth' });
});
```

### 5. Tesseract LSTMモデルのトレーニング

Tesseract 5.x系では、LSTMニューラルネットワークを使ったモデルが標準です。カスタムモデルを作るには、既存の日本語モデルをベースにファインチューニングを行います。

```bash:train/scripts/train_model.sh
# 1. 標準モデルからLSTMを抽出
combine_tessdata -e /usr/local/share/tessdata/jpn.traineddata \
    /workspace/output/jpn_extracted.lstm

# 2. カスタムテキストでトレーニング
lstmtraining \
    --model_output /workspace/output/jpn_custom \
    --continue_from /workspace/output/jpn_extracted.lstm \
    --traineddata /usr/local/share/tessdata/jpn.traineddata \
    --train_listfile /workspace/output/training_files.txt \
    --max_iterations 10000 \
    --learning_rate 0.001

# 3. 最終モデルを生成
lstmtraining \
    --stop_training \
    --continue_from /workspace/output/jpn_custom_checkpoint \
    --traineddata /usr/local/share/tessdata/jpn.traineddata \
    --model_output /workspace/output/jpn_custom.traineddata
```

トレーニングデータは、Pythonスクリプトで日本語テキストから自動生成されます：

```python:train/scripts/generate_training_data.py
# テキストファイルから画像を生成
text2image \
    --text=training_texts_expanded.txt \
    --outputbase=jpn_custom.train \
    --font='Noto Sans CJK JP Regular' \
    --fonts_dir=/workspace/fonts \
    --fontconfig_tmpdir=/tmp

# lstmfファイルを生成
tesseract jpn_custom.train_0000.tif jpn_custom.train_0000 \
    -l jpn \
    --psm 6 \
    lstm.train
```

### 6. GitHub Actionsで自動デプロイ

mainブランチにpushするだけで、自動的にビルド＆GitHub Pagesにデプロイされます。

```yaml:.github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
        working-directory: ./app
      - run: npm run build
        working-directory: ./app
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./app/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
```

カスタムモデルファイル（`jpn_custom.traineddata.gz`）もリポジトリに含めることで、GitHub Pagesでもカスタムモデルが使用できます。

## 使い方

### クイックスタート

```bash
# 1. リポジトリをクローン
git clone https://github.com/tamoco-mocomoco/training-tesseract-js.git
cd training-tesseract-js

# 2. Docker Composeで起動
docker compose up -d

# 3. ブラウザで開く
open http://localhost:3333
```

これだけで、OCRアプリケーションが動作します！

### カスタムモデルをトレーニング

より高精度な認識が必要な場合、カスタムモデルを作成できます：

```bash
# トレーニング用テキストを編集（オプション）
vim train/source/training_texts.txt

# トレーニング実行（30分〜2時間）
bash train/retrain.sh
```

トレーニングが完了すると、ブラウザで「カスタムモデル (jpn_custom)」を選択して試すことができます。

### トレーニングデータのカスタマイズ

特定のドメイン（請求書、領収書など）に特化したモデルを作る場合：

1. `train/source/training_texts.txt` に認識したいテキストを追加
2. 独自のフォント（.ttf/.otf）を `train/fonts/` に配置（オプション）
3. `bash train/retrain.sh` でトレーニング

例えば、請求書OCRなら以下のようなテキストを追加：

```text:train/source/training_texts.txt
株式会社サンプル
〒100-0001 東京都千代田区千代田1-1-1
TEL: 03-1234-5678
ご請求金額: ¥123,456
お支払期限: 2025年1月31日
```

## ハマったポイント

### 1. Web Workerでの関数シリアライズエラー

当初、ログ出力のために`logger`オプションに関数を渡していましたが、Web Workerでは関数をシリアライズできないため、`DataCloneError`が発生しました。

```javascript
// ❌ エラーになる
worker = await createWorker(modelName, {
    logger: m => console.log('[Tesseract]', m)
});

// ✅ loggerオプションを削除
worker = await createWorker(modelName);
```

### 2. Docker volumeマウントの罠

当初、`app/public/tessdata/`に直接モデルファイルを配置していましたが、Docker環境でマウントの問題が発生しました。最終的に`train/output/`を共有ボリュームとして使用することで解決しました。

```yaml:docker-compose.yml
services:
  app:
    volumes:
      - ./train/output:/app/public/tessdata  # 共有ボリューム

  train:
    volumes:
      - ./train/output:/workspace/output     # 同じディレクトリ
```

### 3. GitHub Pagesでのパス問題

絶対パスでlangPathを指定すると、GitHub Pagesでモデルが404になりました。相対パス（`./tessdata`）を使うことで、Viteの`base`設定が自動的に適用され、両環境で動作するようになりました。

## まとめ

Tesseract.jsでカスタムモデルを使った日本語OCRアプリケーションを、トレーニング環境込みで作成しました。

ポイントは以下の通りです：

- **モデルの事前ロード**でUX向上
- **ホワイトリスト機能**でトレーニング不要の文字制限モデルを作成
- **相対パス**で開発環境とGitHub Pages両方に対応
- **Docker Compose**で環境構築を簡単に
- **LSTM fine-tuning**でドメイン特化モデルを作成

同じようにTesseract.jsでカスタムモデルを使いたい方の参考になれば幸いです！

## 参考リンク

- [Tesseract.js Documentation](https://tesseract.projectnaptha.com/)
- [Tesseract OCR Documentation](https://tesseract-ocr.github.io/)
- [Train Your Tesseract](https://tesseract-ocr.github.io/tessdoc/Training-Tesseract.html)
- [GitHub リポジトリ](https://github.com/tamoco-mocomoco/training-tesseract-js)
- [デモサイト](https://tamoco-mocomoco.github.io/training-tesseract-js/)
