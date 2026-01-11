# merge_pdfs.py (pypdf 5.0+ 対応版) + 「全ページを縦長に強制」 + Ghostscript 正規化
import os
import shutil
import subprocess
from pypdf import PdfWriter, PdfReader


def find_ghostscript_executable() -> str:
    candidates = ["gs", "gswin64c", "gswin32c", "gswin64c.exe", "gswin32c.exe"]
    for name in candidates:
        p = shutil.which(name)
        if p:
            return p
    raise FileNotFoundError("Ghostscript が見つかりませんでした。")


def normalize_pdf_with_ghostscript(
    input_pdf: str,
    output_pdf: str,
    compatibility_level: str = "1.4",
    pdfsettings: str = "/prepress",
) -> None:
    gs = find_ghostscript_executable()

    # ★ AutoRotate は None にする（Pythonで決めた向きを壊さない）
    cmd = [
        gs,
        "-dBATCH",
        "-dNOPAUSE",
        "-dSAFER",
        "-sDEVICE=pdfwrite",
        f"-dCompatibilityLevel={compatibility_level}",
        f"-dPDFSETTINGS={pdfsettings}",
        "-dAutoRotatePages=/None",
        f"-sOutputFile={output_pdf}",
        input_pdf,
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(
            "Ghostscript failed.\n"
            f"CMD: {' '.join(cmd)}\n"
            f"STDOUT:\n{r.stdout}\n"
            f"STDERR:\n{r.stderr}\n"
        )


def force_portrait(page) -> None:
    """
    ページを「必ず縦長(ポートレート)になる向き」に強制する。
    /Rotate を考慮した“実効”の幅高さで判定し、横長なら 90 度回す。
    """
    w = float(page.mediabox.width)
    h = float(page.mediabox.height)

    # 現在の回転角（0, 90, 180, 270）
    rot = (page.get("/Rotate") or 0) % 360

    # 回転を考慮した実効サイズ
    if rot in (90, 270):
        eff_w, eff_h = h, w
    else:
        eff_w, eff_h = w, h

    # 横長なら縦長になるまで回す（通常は+90でOK）
    if eff_w > eff_h:
        page.rotate(90)


def merge_pdfs(_input_folder="input", _output_folder="output", _output_filename="merged.pdf"):
    os.makedirs(_output_folder, exist_ok=True)

    writer = PdfWriter()
    pdf_files = sorted([f for f in os.listdir(_input_folder) if f.lower().endswith(".pdf")])

    if not pdf_files:
        print("⚠️ inputフォルダにPDFが見つかりませんでした。")
        return

    print(f"見つかったPDF ({len(pdf_files)}個):")
    for pdf in pdf_files:
        full_path = os.path.join(_input_folder, pdf)
        print(f"  + {pdf}")

        try:
            with open(full_path, "rb") as f:
                reader = PdfReader(f)
                if reader.is_encrypted:
                    reader.decrypt("")

                for page in reader.pages:
                    # ★ここで全ページを縦向きに強制
                    force_portrait(page)
                    writer.add_page(page)

        except Exception as e:
            print(f"❌ {pdf} の処理に失敗: {e}")
            continue

    merged_path = os.path.join(_output_folder, _output_filename)
    with open(merged_path, "wb") as out:
        writer.write(out)
    print(f"\n✅ マージ（向き強制）完了！ → {merged_path}")

    base, ext = os.path.splitext(_output_filename)
    printable_path = os.path.join(_output_folder, f"{base}_printable{ext}")

    normalize_pdf_with_ghostscript(
        input_pdf=merged_path,
        output_pdf=printable_path,
        compatibility_level="1.4",
        pdfsettings="/prepress",
    )
    print(f"✅ 正規化（印刷向け）完了！ → {printable_path}")


if __name__ == "__main__":
    merge_pdfs(_output_filename="week2.pdf")
