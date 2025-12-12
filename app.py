# app.py（ローカル vs 連番 ／ クラウド 上書き 自動切替版）

import streamlit as st
from pathlib import Path
import os
import shutil
from pdfDownloader.download_pdfs_from_page import download_pdfs_from_page
from pdfMerger.merge_pdf import merge_pdfs
import urllib.robotparser

st.set_page_config(
    page_title="PDF吸い取り＋結合マシーン",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.error("""
【重要：必ずお読みください】
・このツールは「公開されているPDFリンク」のみを対象としています
・ログインが必要なページ・利用規約で自動取得を禁止しているサイトは絶対に使用しないでください
・著作権侵害になる使い方は一切禁止です。使用者は自己責任でお願いします
・開発者は一切の責任を負いません
""")


# ==================== 環境自動判別 ====================
def is_running_on_streamlit_cloud():
    """Streamlit Cloudで動いてるか判定（秘密鍵があるかどうか）"""
    return "STREAMLIT_CLOUD" in os.environ or os.getenv("IS_STREAMLIT_CLOUD")


IS_CLOUD = is_running_on_streamlit_cloud()


# ==================== Chrome風連番関数（ローカル専用） ====================
def get_unique_filename(directory, filename):
    if IS_CLOUD:
        return os.path.join(directory, filename)  # クラウドは上書き

    path = Path(directory) / filename
    if not path.exists():
        return str(path)

    stem = path.stem
    suffix = path.suffix
    counter = 1
    while True:
        new_name = f"{stem}({counter}){suffix}"
        new_path = path.parent / new_name
        if not new_path.exists():
            return str(new_path)
        counter += 1


# ==================== 保存先設定 ====================
def get_downloads_folder():
    return str(Path.home() / "Downloads")


save_dir = get_downloads_folder()

st.title("ページの全PDFをダウンロード → 1つのPDFに結合！")

# クラウドではフォルダ選択無効化
if IS_CLOUD:
    st.info("クラウド環境：完成PDFは下のダウンロードボタンで取得してください（自動保存はされません）")
else:
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
            pass

st.caption(f"保存先 → **{save_dir if not IS_CLOUD else 'クラウド上（一時的）'}**")

# ==================== 入力 ====================
col1, col2 = st.columns([2, 1])
with col1:
    url = st.text_input("PDFが載ってるページのURL",
                        value="https://xn--fdk3a7ctb5192box5b.com/yo/oekaki/ewonazoru_step1.html")
with col2:
    final_name = st.text_input("完成PDFの名前", value="統合済プリント")

    # final_name を入力してもらったあとに、.pdf がなかったら自動付与
    if not final_name.lower().endswith('.pdf'):
        final_name += '.pdf'


def is_allowed(_url):
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url("/".join(_url.split("/")[:3]) + "/robots.txt")
        rp.read()
        return rp.can_fetch("*", _url)
    except:
        return True


if st.button("全PDFダウンロード → 結合 → 完成！！", type="primary", use_container_width=True):

    # 利用可能なウェブサイトでのみ利用OK
    if "login" in url or "member" in url:
        st.error("ログインが必要なページは使用禁止です")
        st.stop()
    if not is_allowed(url):
        st.error("このサイトは自動取得を禁止しています")
        st.stop()

    if not url.strip():
        st.error("URLを入力してください！")
        st.stop()

    temp_folder = "temp_pdfs_merge"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
    os.makedirs(temp_folder, exist_ok=True)

    # ダウンロード
    with st.spinner("PDFをダウンロード中..."):
        try:
            download_pdfs_from_page(url, temp_folder)
            pdf_files = [os.path.join(temp_folder, f) for f in os.listdir(temp_folder)
                         if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(temp_folder, f))]
            if not pdf_files:
                st.error("PDFが見つかりませんでした")
                shutil.rmtree(temp_folder, ignore_errors=True)
                st.stop()
            st.success(f"{len(pdf_files)}個ダウンロード完了！")
        except Exception as e:
            st.error(f"ダウンロード失敗: {e}")
            shutil.rmtree(temp_folder, ignore_errors=True)
            st.stop()

    # 最終ファイルパス決定（ローカル 連番／クラウド 上書き）
    final_path = get_unique_filename(save_dir, final_name)

    # 結合
    with st.spinner("PDFを結合中..."):
        try:
            merge_pdfs(
                _input_folder=temp_folder,
                _output_folder=os.path.dirname(final_path),
                _output_filename=os.path.basename(final_path)
            )
            st.success("結合成功！！")
            st.balloons()
        except Exception as e:
            st.error(f"結合失敗: {e}")
            st.stop()
        finally:
            shutil.rmtree(temp_folder, ignore_errors=True)

    # ダウンロードボタン（常に表示）
    with open(final_path, "rb") as f:
        st.download_button(
            label="完成PDFを今すぐダウンロード！！",
            data=f.read(),
            file_name=os.path.basename(final_path),
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

    if IS_CLOUD:
        st.info("クラウド環境：ファイルは一時的です。必ず上のボタンでダウンロードしてください！")
    else:
        st.info(f"保存完了 → `{final_path}`{'（連番付き）' if '(1)' in final_path or '(2)' in final_path else ''}")

st.markdown("---")
if IS_CLOUD:
    st.caption("クラウドモード：毎回上書き＋ダウンロードボタン必須")
else:
    st.caption("ローカルモード：ダウンロードフォルダに連番付きで自動保存！")