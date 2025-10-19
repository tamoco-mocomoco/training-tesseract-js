#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tesseract用の日本語トレーニングデータを生成するスクリプト（text2image版・並列化対応）
"""

import os
import subprocess
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import tempfile
import time

# 設定
OUTPUT_DIR = "/workspace/data"
FONT_DIR = "/workspace/fonts"
TRAINING_TEXT_FILE = "/workspace/source/training_texts_expanded.txt"
MODEL_NAME = "jpn_custom"
FONT_SIZE = 48


def get_available_fonts():
    """利用可能な日本語フォントを取得"""
    # text2imageで使用できる日本語フォント名（ファミリー名）
    fonts = [
        "IPAexGothic",
        "IPAexMincho",
        "TakaoGothic",
        "TakaoMincho",
        "TakaoPGothic",
        "Noto Sans CJK JP",
        "Noto Serif CJK JP",
    ]

    print("Available fonts:")
    for font in fonts:
        print(f"  - {font}")

    return fonts


def load_training_texts():
    """トレーニング用テキストを読み込む"""
    texts = []

    if os.path.exists(TRAINING_TEXT_FILE):
        with open(TRAINING_TEXT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 空行とコメント行をスキップ
                if line and not line.startswith('#'):
                    texts.append(line)
        print(f"Loaded {len(texts)} texts from {TRAINING_TEXT_FILE}")
    else:
        print(f"Error: {TRAINING_TEXT_FILE} not found")

    return texts


def generate_single_image(args):
    """単一の画像を生成（並列処理用）"""
    text, font_name, image_index = args

    base_name = f"{MODEL_NAME}.train_{image_index:04d}"
    output_base = os.path.join(OUTPUT_DIR, base_name)

    # テキストを一時ファイルに書き出す
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
        f.write(text)
        text_file = f.name

    try:
        # text2imageコマンドで画像とボックスファイルを生成
        cmd = [
            'text2image',
            '--text', text_file,
            '--outputbase', output_base,
            '--font', font_name,
            '--fonts_dir', '/usr/share/fonts',
            '--ptsize', str(FONT_SIZE),
            '--leading', '48',
            '--char_spacing', '1.0',
            '--exposure', '0',
            '--resolution', '300',
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return (True, None, image_index)

    except subprocess.CalledProcessError as e:
        return (False, f"Text: {text[:30]}..., Font: {font_name}, Error: {e.stderr}", image_index)
    finally:
        # 一時ファイルを削除
        if os.path.exists(text_file):
            os.unlink(text_file)


def generate_training_data_with_text2image(texts, fonts, max_workers=None):
    """text2imageコマンドでトレーニングデータを並列生成"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # CPU数を取得
    if max_workers is None:
        # 環境変数で指定可能、デフォルトはCPU数の2倍（I/O待ちが多いため）
        max_workers = int(os.environ.get('MAX_WORKERS', multiprocessing.cpu_count() * 2))
        max_workers = max(1, max_workers)

    print(f"並列処理を開始（ワーカー数: {max_workers}）", flush=True)

    # タスクリストを作成
    tasks = []
    image_index = 0
    for text in texts:
        for font_name in fonts:
            tasks.append((text, font_name, image_index))
            image_index += 1

    total_tasks = len(tasks)
    print(f"総タスク数: {total_tasks}", flush=True)

    # 並列処理
    total_images = 0
    failed_images = 0
    failed_details = []

    start_time = time.time()
    last_print_time = start_time

    print("処理を開始しています...\n", flush=True)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # タスクを投入
        futures = {executor.submit(generate_single_image, task): task for task in tasks}

        # 進捗表示
        completed = 0
        for future in as_completed(futures):
            completed += 1
            success, error, idx = future.result()

            if success:
                total_images += 1
            else:
                failed_images += 1
                if len(failed_details) < 5:  # 最初の5件のみ保存
                    failed_details.append(error)

            # 進捗を表示（50個ごと、または3秒ごと、または完了時）
            current_time = time.time()
            should_print = (
                completed % 50 == 0 or
                completed == total_tasks or
                (current_time - last_print_time) >= 3.0
            )

            if should_print:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (total_tasks - completed) / rate if rate > 0 else 0
                print(f"進捗: {completed}/{total_tasks} ({completed*100/total_tasks:.1f}%) "
                      f"| 成功: {total_images}, 失敗: {failed_images} "
                      f"| 速度: {rate:.1f}枚/秒 | 残り時間: {remaining/60:.1f}分", flush=True)
                last_print_time = current_time

    # エラー詳細を表示
    if failed_details:
        print("\n最初の失敗例:")
        for detail in failed_details:
            print(f"  - {detail}")

    return total_images, failed_images


def main():
    """メイン処理"""
    print("=== Tesseract トレーニングデータ生成（text2image版） ===\n")

    # フォントの取得
    print("Available fonts:")
    fonts = get_available_fonts()
    if not fonts:
        print("Error: No Japanese fonts found!")
        return

    print(f"\nFound {len(fonts)} Japanese fonts\n")

    # テキストの読み込み
    texts = load_training_texts()
    if not texts:
        print("Error: No training texts loaded!")
        return

    print(f"\n=== トレーニングデータ生成開始 ===")
    print(f"テキスト数: {len(texts)}")
    print(f"フォント数: {len(fonts)}")
    print(f"予想画像数: 約{len(texts) * len(fonts)}枚")
    print()

    # データ生成
    total, failed = generate_training_data_with_text2image(texts, fonts)

    print(f"\n=== 完了 ===")
    print(f"成功: {total}枚")
    print(f"失敗: {failed}枚")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"\n次のステップ: train_model.sh を実行してモデルトレーニング")


if __name__ == "__main__":
    main()
