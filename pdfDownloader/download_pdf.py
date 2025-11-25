import os
import requests
from tqdm import tqdm  # 進捗バーを表示（なくてもOK）

# ==================== 設定ここから ====================
# ベースURL（連番の前まで）
base_url = "http://meiro.moo.jp/meiro/meiro"

# ファイル拡張子
extension = ".pdf"

# 開始番号と終了番号（両方含む）
start_num = 1
end_num = 43

# 出力フォルダ
output_dir = "output"

# 番号の桁数（例: 001, 002 → 3桁）
# 実際のURLに合わせて調整（meiro001.pdf なら 3）
padding = 3
# ==================== 設定ここまで ====================

# 出力フォルダがなければ作成
os.makedirs(output_dir, exist_ok=True)

# 進捗バー付きでループ
for num in tqdm(range(start_num, end_num + 1), desc="Downloading"):
    # 番号をゼロ埋めして文字列に変換（例: 1 → "001"）
    num_str = f"{num:0{padding}d}"
    filename = f"meiro{num_str}{extension}"
    url = f"{base_url}{num_str}{extension}"
    save_path = os.path.join(output_dir, filename)

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
print(f"保存先: {os.path.abspath(output_dir)}")