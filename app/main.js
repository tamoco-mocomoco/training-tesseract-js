import { createWorker } from 'tesseract.js';

// DOM要素の取得
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const previewSection = document.getElementById('preview-section');
const previewImage = document.getElementById('preview-image');
const processBtn = document.getElementById('process-btn');
const progressSection = document.getElementById('progress-section');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultSection = document.getElementById('result-section');
const resultText = document.getElementById('result-text');
const confidenceEl = document.getElementById('confidence');
const processingTimeEl = document.getElementById('processing-time');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const resetBtn = document.getElementById('reset-btn');
const rerunBtn = document.getElementById('rerun-btn');
const modelSelect = document.getElementById('model-select');

// 状態管理
let currentImage = null;
let worker = null;
let startTime = null;
let isWorkerReady = false;
let isLoadingWorker = false;

// ファイル選択のイベントリスナー
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

// ドラッグ&ドロップのイベントリスナー
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);
    }
});

// ドロップゾーンクリックでファイル選択
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// fileLabelは<label for="file-input">なので、自動的にfileInputをクリックする
// 追加のイベントリスナーは不要（削除）

// ファイル処理
function handleFile(file) {
    const reader = new FileReader();

    reader.onload = (e) => {
        currentImage = e.target.result;
        previewImage.src = currentImage;
        previewSection.style.display = 'block';
        resultSection.style.display = 'none';
        progressSection.style.display = 'none';
    };

    reader.readAsDataURL(file);
}

// Workerの作成（モデル選択時とOCR実行時に使用）
async function createModelWorker(modelName) {
    console.log('[Tesseract] Creating worker for model:', modelName);

    if (modelName === 'jpn_custom') {
        return await createWorker(modelName, 1, {
            langPath: './tessdata'
        });
    } else {
        return await createWorker(modelName);
    }
}

// モデル選択時のWorker事前作成
modelSelect.addEventListener('change', async () => {
    const selectedModel = modelSelect.value;

    // 既に読み込み中の場合は何もしない
    if (isLoadingWorker) {
        console.log('[Tesseract] Already loading a worker, skipping...');
        return;
    }

    isLoadingWorker = true;
    isWorkerReady = false;

    try {
        // 既存のWorkerがあれば終了
        if (worker) {
            console.log('[Tesseract] Terminating existing worker for model switch...');
            await worker.terminate();
            worker = null;
        }

        console.log('[Tesseract] Pre-loading model:', selectedModel);
        worker = await createModelWorker(selectedModel);
        isWorkerReady = true;
        console.log('[Tesseract] Model ready:', selectedModel);
    } catch (error) {
        console.error('[Tesseract] Failed to pre-load model:', error);
        worker = null;
        isWorkerReady = false;
    } finally {
        isLoadingWorker = false;
    }
});

// OCR実行ボタン
processBtn.addEventListener('click', async () => {
    if (!currentImage) return;

    // 画像は表示したまま、結果セクションだけ非表示
    resultSection.style.display = 'none';
    progressSection.style.display = 'block';

    startTime = Date.now();

    await performOCR(currentImage);
});

// OCR処理
async function performOCR(image) {
    try {
        const selectedModel = modelSelect.value;

        // Workerが準備されていない場合は作成
        if (!isWorkerReady || !worker) {
            console.log('[Tesseract] Worker not ready, creating now...');

            // 既存のWorkerがあれば先に終了させる
            if (worker) {
                try {
                    await worker.terminate();
                } catch (e) {
                    console.warn('[Tesseract] Failed to terminate existing worker:', e);
                }
                worker = null;
            }

            progressText.textContent = 'Tesseractを初期化中...';
            progressFill.style.width = '10%';

            progressText.textContent = `言語データ (${selectedModel}) を読み込み中...`;
            progressFill.style.width = '30%';

            worker = await createModelWorker(selectedModel);
            isWorkerReady = true;
        } else {
            console.log('[Tesseract] Using pre-loaded worker');
            progressText.textContent = 'テキストを認識中...';
            progressFill.style.width = '30%';
        }

        progressText.textContent = 'テキストを認識中...';
        progressFill.style.width = '70%';

        // OCR実行
        const { data: { text, confidence } } = await worker.recognize(image);

        // 処理完了
        progressFill.style.width = '100%';
        progressText.textContent = '完了！';

        const processingTime = ((Date.now() - startTime) / 1000).toFixed(2);

        // 結果表示
        setTimeout(() => {
            displayResult(text, confidence, processingTime);
        }, 500);

        // Workerの終了
        await worker.terminate();
        worker = null;

    } catch (error) {
        console.error('[OCR Error] Full error:', error);
        console.error('[OCR Error] Message:', error.message);
        console.error('[OCR Error] Stack:', error.stack);

        progressText.textContent = `エラー: ${error.message}`;

        // より詳細なエラーメッセージを表示
        const errorDetails = `OCR処理中にエラーが発生しました。\n\nエラー: ${error.message}\n\nコンソールで詳細を確認してください。`;
        alert(errorDetails);

        if (worker) {
            await worker.terminate();
            worker = null;
        }
    }
}

// 結果表示
function displayResult(text, confidence, processingTime) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';

    resultText.value = text;
    confidenceEl.textContent = `${confidence.toFixed(2)}%`;
    processingTimeEl.textContent = `${processingTime}秒`;
}

// コピーボタン
copyBtn.addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(resultText.value);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'コピーしました！';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    } catch (error) {
        alert('コピーに失敗しました');
    }
});

// ダウンロードボタン
downloadBtn.addEventListener('click', () => {
    const text = resultText.value;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ocr-result.txt';
    a.click();
    URL.revokeObjectURL(url);
});

// 再実行ボタン（別のモデルで再度OCR）
rerunBtn.addEventListener('click', () => {
    // 結果セクションを非表示にしてプレビューセクションにスクロール
    resultSection.style.display = 'none';
    progressSection.style.display = 'none';

    // プレビューセクションまでスムーズスクロール
    previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// リセットボタン
resetBtn.addEventListener('click', async () => {
    // Workerのクリーンアップ
    if (worker) {
        try {
            await worker.terminate();
            worker = null;
        } catch (e) {
            console.warn('[Reset] Failed to terminate worker:', e);
        }
    }

    // 状態フラグのリセット
    isWorkerReady = false;
    isLoadingWorker = false;

    currentImage = null;
    previewSection.style.display = 'none';
    resultSection.style.display = 'none';
    progressSection.style.display = 'none';
    fileInput.value = '';
    resultText.value = '';

    // デフォルトモデルを再度読み込み
    const defaultModel = modelSelect.value;
    isLoadingWorker = true;
    try {
        worker = await createModelWorker(defaultModel);
        isWorkerReady = true;
        console.log('[Reset] Model reloaded:', defaultModel);
    } catch (error) {
        console.error('[Reset] Failed to reload model:', error);
    } finally {
        isLoadingWorker = false;
    }
});

// 初期化
console.log('Japanese OCR App initialized');

// ページロード時にデフォルトモデルを事前読み込み
(async () => {
    const defaultModel = modelSelect.value;
    console.log('[Tesseract] Pre-loading default model on page load:', defaultModel);

    isLoadingWorker = true;
    try {
        worker = await createModelWorker(defaultModel);
        isWorkerReady = true;
        console.log('[Tesseract] Default model ready:', defaultModel);
    } catch (error) {
        console.error('[Tesseract] Failed to load default model:', error);
        isWorkerReady = false;
    } finally {
        isLoadingWorker = false;
    }
})();
