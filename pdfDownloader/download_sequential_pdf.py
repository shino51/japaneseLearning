import os
import requests
from tqdm import tqdm  # 進捗バーを表示（なくてもOK）
import shutil


# 番号の桁数（例: 001, 002 → 3桁）
# padding は実際のURLに合わせて調整（meiro001.pdf なら 3）
def download_sequential_pdf(_base_url, _output_dir="output", _start_num=1, _end_num=100, _padding=3):
    # ファイル拡張子
    extension = ".pdf"

    # 出力フォルダを完全に削除してから作り直す（毎回まっさらな状態に！）
    if os.path.exists(_output_dir):
        print(f"古いフォルダを削除中 → {_output_dir}")
        shutil.rmtree(_output_dir)  # 中身ごと全部削除
    os.makedirs(_output_dir, exist_ok=True)

    # 進捗バー付きでループ
    for num in tqdm(range(_start_num, _end_num + 1), desc="Downloading"):
        # 番号をゼロ埋めして文字列に変換（例: 1 → "001"）
        num_str = f"{num:0{_padding}d}"
        filename = f"meiro{num_str}{extension}"
        url = f"{_base_url}{num_str}{extension}"
        save_path = os.path.join(_output_dir, filename)

        # すでにダウンロード済みの場合はスキップ（必要ならコメントアウト）
        if os.path.exists(save_path):
            # tqdm.write(f"Skipped (already exists): {filename}")
            continue

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                # tqdm.write(f"Downloaded: {filename}")
            else:
                print(f"Not found (skipping): {url} → {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error on {url}: {e}")

    print("\nダウンロード完了！")
    print(f"保存先: {os.path.abspath(_output_dir)}")


if __name__ == "__main__":
    # ベースURL（連番の前まで）
    base_url = "http://meiro.moo.jp/meiro/meiro"
    # 終了番号
    end_num = 43

    download_sequential_pdf(base_url, _end_num=end_num)
