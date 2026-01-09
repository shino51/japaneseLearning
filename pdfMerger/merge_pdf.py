# merge_pdfs.py  (pypdf 5.0+ 対応版) + Ghostscript 正規化
import os
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pypdf import PdfWriter  # IDE用型ヒント

from pypdf import PdfWriter, PdfReader  # 実行用（Readerも追加でページ単位対応）


def find_ghostscript_executable() -> str:
    """
    Ghostscript の実行ファイルをPATHから探す。
    Windowsなら gswin64c / gswin32c、mac/Linuxなら gs が入ることが多い。
    """
    candidates = [
        "gs",            # macOS/Linux
        "gswin64c",      # Windows (console)
        "gswin32c",      # Windows (console)
        "gswin64c.exe",
        "gswin32c.exe",
    ]
    for name in candidates:
        p = shutil.which(name)
        if p:
            return p
    raise FileNotFoundError(
        "Ghostscript が見つかりませんでした。\n"
        "Windows: Ghostscript をインストールして PATH を通すか、gswin64c.exe のフルパスを指定してください。\n"
        "macOS: brew install ghostscript\n"
        "Linux: sudo apt install ghostscript"
    )


def normalize_pdf_with_ghostscript(
    input_pdf: str,
    output_pdf: str,
    compatibility_level: str = "1.4",
    pdfsettings: str = "/prepress",
) -> None:
    """
    Ghostscript でPDFを正規化（印刷互換性を上げるために再生成）する。
    """
    gs = find_ghostscript_executable()

    cmd = [
        gs,
        "-dBATCH",
        "-dNOPAUSE",
        "-dSAFER",
        "-sDEVICE=pdfwrite",
        f"-dCompatibilityLevel={compatibility_level}",
        f"-dPDFSETTINGS={pdfsettings}",
        f"-sOutputFile={output_pdf}",
        input_pdf,
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)

    if r.returncode != 0:
        raise RuntimeError(
            "Ghostscript による正規化に失敗しました。\n"
            f"Command: {' '.join(cmd)}\n"
            f"STDOUT:\n{r.stdout}\n"
            f"STDERR:\n{r.stderr}\n"
        )


def merge_pdfs(_input_folder="input", _output_folder="output", _output_filename="merged.pdf"):
    # フォルダがなければ作成
    if not os.path.exists(_output_folder):
        print(f"新しいフォルダを作成中 → {_output_folder}")
        os.makedirs(_output_folder, exist_ok=True)

    writer = PdfWriter()  # PdfMerger → PdfWriter

    # inputフォルダ内のPDFファイルを名前順に取得
    pdf_files = sorted([f for f in os.listdir(_input_folder) if f.lower().endswith(".pdf")])

    if not pdf_files:
        print("⚠️  inputフォルダにPDFが見つかりませんでした。")
        return

    print(f"見つかったPDF ({len(pdf_files)}個):")
    for pdf in pdf_files:
        full_path = os.path.join(_input_folder, pdf)
        print(f"  + {pdf}")
        try:
            # ファイルパスを直接append（PdfWriterも対応）
            writer.append(full_path)
        except Exception as e:
            print(f"❌ {pdf} のマージ失敗: {e}")
            # 代替: ページ単位で追加（壊れたPDF対応）
            try:
                with open(full_path, "rb") as f:
                    reader = PdfReader(f)
                    if reader.is_encrypted:
                        reader.decrypt("")  # パスワードなしの場合
                    for page in reader.pages:
                        writer.add_page(page)
            except Exception as e2:
                print(f"❌ 代替追加も失敗: {e2}")
                continue

    output_path = os.path.join(_output_folder, _output_filename)

    # 1) まず通常のマージPDFを書き出し
    try:
        with open(output_path, "wb") as out:
            writer.write(out)
        print(f"\n✅ マージ完了！ → {output_path}")
    except Exception as e:
        print(f"❌ 出力失敗: {e}")
        return

    # 2) Ghostscriptで「印刷向け正規化PDF」を生成
    base, ext = os.path.splitext(_output_filename)
    printable_name = f"{base}_printable{ext}"
    printable_path = os.path.join(_output_folder, printable_name)

    try:
        # 互換性重視なら 1.4 が無難。画質/サイズが気になるなら pdfsettings を /printer や /ebook に変更
        normalize_pdf_with_ghostscript(
            input_pdf=output_path,
            output_pdf=printable_path,
            compatibility_level="1.4",
            pdfsettings="/prepress",
        )
        print(f"✅ 正規化（印刷向け）完了！ → {printable_path}")
    except Exception as e:
        print("⚠️ Ghostscript 正規化に失敗しました。マージPDFは作成済みです。")
        print(e)


if __name__ == "__main__":
    output_name = "merged.pdf"
    merge_pdfs(_output_filename=output_name)
