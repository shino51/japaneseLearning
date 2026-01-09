# merge_pdfs.py (pypdf 5.0+ 対応版) + 方向統一 + Ghostscript 正規化
import os
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pypdf import PdfWriter

from pypdf import PdfWriter, PdfReader


def find_ghostscript_executable() -> str:
    candidates = ["gs", "gswin64c", "gswin32c", "gswin64c.exe", "gswin32c.exe"]
    for name in candidates:
        p = shutil.which(name)
        if p:
            return p
    raise FileNotFoundError(
        "Ghostscript が見つかりませんでした。packages.txt に ghostscript を入れているか確認してください。"
    )


def normalize_pdf_with_ghostscript(
    input_pdf: str,
    output_pdf: str,
    compatibility_level: str = "1.4",
    pdfsettings: str = "/prepress",
    autorotate_pages: str = "/PageByPage",
) -> None:
    """
    GhostscriptでPDFを再生成して正規化する。
    autorotate_pages を /PageByPage にすると、ページごとに自動回転して「読みやすい向き」に揃えやすい。
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
        f"-dAutoRotatePages={autorotate_pages}",  # ★向き揃え（重要）
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


def merge_pdfs(
    _input_folder="input",
    _output_folder="output",
    _output_filename="merged.pdf",
    rotate_landscape_to_portrait: bool = False,
):
    # フォルダがなければ作成
    if not os.path.exists(_output_folder):
        print(f"新しいフォルダを作成中 → {_output_folder}")
        os.makedirs(_output_folder, exist_ok=True)

    writer = PdfWriter()

    pdf_files = sorted([f for f in os.listdir(_input_folder) if f.lower().endswith(".pdf")])
    if not pdf_files:
        print("⚠️  inputフォルダにPDFが見つかりませんでした。")
        return

    print(f"見つかったPDF ({len(pdf_files)}個):")
    for pdf in pdf_files:
        full_path = os.path.join(_input_folder, pdf)
        print(f"  + {pdf}")

        # append がうまくいくなら最速
        if not rotate_landscape_to_portrait:
            try:
                writer.append(full_path)
                continue
            except Exception as e:
                print(f"❌ {pdf} のマージ失敗(append): {e}")
                print("   → ページ単位で追加に切り替えます")

        # ページ単位で追加（必要なら向きも調整）
        try:
            with open(full_path, "rb") as f:
                reader = PdfReader(f)
                if reader.is_encrypted:
                    reader.decrypt("")

                for page in reader.pages:
                    if rotate_landscape_to_portrait:
                        w = float(page.mediabox.width)
                        h = float(page.mediabox.height)
                        # 横長なら90度回転（ページ属性Rotateを付ける形）
                        if w > h:
                            page.rotate(90)

                    writer.add_page(page)

        except Exception as e2:
            print(f"❌ ページ単位追加も失敗: {e2}")
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

    # 2) Ghostscriptで「向き揃え + 印刷向け正規化PDF」を生成
    base, ext = os.path.splitext(_output_filename)
    printable_name = f"{base}_printable{ext}"
    printable_path = os.path.join(_output_folder, printable_name)

    try:
        normalize_pdf_with_ghostscript(
            input_pdf=output_path,
            output_pdf=printable_path,
            compatibility_level="1.4",
            pdfsettings="/prepress",
            autorotate_pages="/PageByPage",  # ★ここで向きを揃える
        )
        print(f"✅ 向き揃え + 正規化（印刷向け）完了！ → {printable_path}")
    except Exception as e:
        print("⚠️ Ghostscript 正規化に失敗しました。マージPDFは作成済みです。")
        print(e)


if __name__ == "__main__":
    output_name = "week1.pdf"

    # rotate_landscape_to_portrait=False が基本おすすめ（向き揃えはGhostscriptに任せる）
    # もし元PDFが壊れ気味で append が落ちる/向きが変になるなら True を試してOK
    merge_pdfs(_output_filename=output_name, rotate_landscape_to_portrait=False)
