import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import shutil


def download_pdfs_from_page(_target_url, _output_dir="output"):
    target_ext = ".pdf"

    if not os.path.exists(_output_dir):
        os.makedirs(_output_dir, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    print(f"ページ読み込み中 → {_target_url}")
    response = session.get(_target_url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # PDFリンク収集
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().endswith(target_ext):
            full_url = urljoin(_target_url, href)
            pdf_links.append(full_url)

    pdf_links = list(set(pdf_links))  # 重複除去

    if not pdf_links:
        print("PDFリンクが見つかりませんでした")
        exit()

    print(f"{len(pdf_links)}個のPDFを発見 → ダウンロード開始！\n")

    # ダウンロード
    for url in tqdm(pdf_links, desc="Downloading", unit="file"):
        filename = os.path.basename(urlparse(url).path)
        save_path = os.path.join(_output_dir, filename)

        try:
            r = session.get(url, timeout=30)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
            tqdm.write(f"ダウンロード完了: {filename}")
        except Exception as e:
            tqdm.write(f"失敗: {filename} → {e}")

    print("すべて完了！")
    print(f"保存先 → {os.path.abspath(_output_dir)}")
    print(f"合計 {len([f for f in os.listdir(_output_dir) if f.endswith(target_ext)])} ファイル")


if __name__ == "__main__":
    # ==================== 設定ここから ====================
    target_url = "https://xn--fdk3a7ctb5192box5b.com/yo/unpitsu/senwohiku1_step1.html"
    output_dir = "input"
    download_pdfs_from_page(target_url, output_dir)
