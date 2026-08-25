# merge_pdfs.py (pypdf 5.0+ 対応版) + 「全ページを縦長に強制」 + Ghostscript 正規化
import os
import shutil
import subprocess
from pypdf import PdfWriter, PdfReader
import zipfile
from PIL import Image


def merge_pdfs(_input_folder="input", _output_folder="output", _output_filename="merged.pdf"):
    os.makedirs(_output_folder, exist_ok=True)

    # Check for ZIP files in the input folder
    zip_files = [f for f in os.listdir(_input_folder) if f.lower().endswith(".zip")]
    if zip_files:
        for zip_file in zip_files:
            zip_path = os.path.join(_input_folder, zip_file)
            extract_zip(zip_path, _input_folder)

    # Convert images to PDFs
    convert_images_to_pdfs(_input_folder)

    writer = PdfWriter()
    # pdf_files = sorted([f for f in os.listdir(_input_folder) if f.lower().endswith(".pdf")])

    # Recursively find all PDF files in the input folder and its subdirectories
    pdf_files = []
    for root, _, files in os.walk(_input_folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    pdf_files.sort()  # Sort the files for consistent order

    if not pdf_files:
        print("⚠️ inputフォルダにPDFが見つかりませんでした。")
        return

    print(f"見つかったPDF ({len(pdf_files)}個):")
    for pdf in pdf_files:
        print(f"  + {pdf}")

        try:
            with open(pdf, "rb") as f:  # Use the correct full path directly
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


def convert_images_to_pdfs(input_folder):
    """
    Converts all image files in the input folder to PDFs.
    """
    image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(image_extensions)]

    for image_file in image_files:
        image_path = os.path.join(input_folder, image_file)
        pdf_path = os.path.splitext(image_path)[0] + ".pdf"

        try:
            with Image.open(image_path) as img:
                # Convert image to RGB mode if not already
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(pdf_path, "PDF", resolution=100.0)
            print(f"✅ 画像をPDFに変換しました: {image_file} → {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"❌ 画像のPDF変換に失敗しました: {image_file} - {e}")


def extract_zip(zip_path, extract_to):
    """
    Extracts a ZIP file to the specified directory.
    """
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"{zip_path} is not a valid ZIP file.")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✅ ZIPファイルを展開しました: {zip_path} → {extract_to}")


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


if __name__ == "__main__":
    merge_pdfs(_output_filename="week13.pdf")
