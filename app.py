# app.py（Chrome風連番自動付与 + すべてのバグ完全殲滅版）

import streamlit as st
from pathlib import Path
import os
import shutil
from pdfDownloader.download_pdfs_from_page import download_pdfs_from_page
from pdfMerger.merge_pdf import merge_pdfs

# 最初に書く〜〜！！！
st.set_page_config(
    page_title="PDF吸い取り＋結合マシーン",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ダウンロードフォルダ取得
def get_downloads_folder():
    return str(Path.home() / "Downloads")


# Chrome風連番付与関数（神）
def get_unique_filename(directory, filename):
    """完成した絵本.pdf → 完成した絵本(1).pdf, (2).pdf... みたいにする"""
    path = Path(directory) / filename
    if not path.exists():
        return str(path)

    stem = path.stem  # "完成した絵本"
    suffix = path.suffix  # ".pdf"

    counter = 1
    while True:
        new_name = f"{stem}({counter}){suffix}"
        new_path = path.parent / new_name
        if not new_path.exists():
            return str(new_path)
        counter += 1


# 保存先設定
save_dir = get_downloads_folder()

st.title("ページの全PDFをダウンロード → 1つのPDFに結合！")

change_folder = st.checkbox("保存先フォルダを変更する（デフォルト：ダウンロードフォルダ）")

if change_folder:
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        selected = filedialog.askdirectory(title="保存先を選択", initialdir=save_dir)
        if selected:
            save_dir = selected
    except:
        st.warning("フォルダ選択はローカル環境のみです")

st.caption(f"保存先 → **{save_dir}**")

col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input(
        "PDFが載ってるページのURL",
        value="https://xn--fdk3a7ctb5192box5b.com/yo/oekaki/ewonazoru_step1.html"
    )

with col2:
    base_name = st.text_input("完成PDFの名前（連番自動付与）", value="統合プリント.pdf")

if st.button("全PDFダウンロード → 結合 → 保存！！", type="primary", use_container_width=True):
    if not url.strip():
        st.error("URLを入力してください！")
        st.stop()

    temp_folder = "temp_pdfs_merge"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
    os.makedirs(temp_folder, exist_ok=True)

    # 1. ダウンロード
    with st.spinner("PDFをダウンロード中..."):
        try:
            download_pdfs_from_page(url, temp_folder)
            pdf_files = [
                os.path.join(temp_folder, f) for f in os.listdir(temp_folder)
                if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(temp_folder, f))
            ]
            if not pdf_files:
                st.error("PDFが見つかりませんでした")
                shutil.rmtree(temp_folder, ignore_errors=True)
                st.stop()
            st.success(f"{len(pdf_files)}個ダウンロード完了！")
        except Exception as e:
            st.error(f"ダウンロード失敗: {e}")
            shutil.rmtree(temp_folder, ignore_errors=True)
            st.stop()

    # 2. 結合 + Chrome風連番付与
    final_path = get_unique_filename(save_dir, base_name)  # ← ここが神！

    with st.spinner("PDFを結合中..."):
        try:
            merge_pdfs(
                _input_folder=temp_folder,
                _output_folder=os.path.dirname(final_path),  # フォルダ
                _output_filename=os.path.basename(final_path)  # ファイル名（(1).pdf付き）
            )
            st.success("結合成功！")
            st.balloons()
        except Exception as e:
            st.error(f"結合失敗: {e}")
            st.stop()
        finally:
            shutil.rmtree(temp_folder, ignore_errors=True)

    # 3. ダウンロードボタン
    if os.path.exists(final_path):
        with open(final_path, "rb") as f:
            st.download_button(
                label="完成PDFを今すぐダウンロード！！",
                data=f.read(),
                file_name=os.path.basename(final_path),
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        st.info(f"保存完了 → `{final_path}`")
    else:
        st.warning("クラウド環境では保存先は見えませんが、ダウンロードボタンで入手できます！")

st.markdown("---")
st.caption("Chromeと同じ！同じ名前のファイルがあっても上書きせず (1), (2)... を自動付与")