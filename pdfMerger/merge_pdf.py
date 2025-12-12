# merge_pdfs.py  (pypdf 5.0+ 対応版)
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pypdf import PdfWriter  # IDE用型ヒント

from pypdf import PdfWriter, PdfReader  # 実行用（Readerも追加でページ単位対応）
import shutil


def merge_pdfs(_input_folder="input", _output_folder="output", _output_filename="merged.pdf"):
    # フォルダがなければ作成
    if not os.path.exists(_output_folder):
        print(f"新しいフォルダを作成中 → {_output_folder}")
        os.makedirs(_output_folder, exist_ok=True)

    writer = PdfWriter()  # PdfMerger → PdfWriter に変更！

    # inputフォルダ内のPDFファイルを名前順に取得
    pdf_files = sorted([f for f in os.listdir(_input_folder) if f.lower().endswith('.pdf')])

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
    try:
        with open(output_path, "wb") as out:  # with文で安全に書き込み
            writer.write(out)
        print(f"\n✅ マージ完了！ → {output_path}")
    except Exception as e:
        print(f"❌ 出力失敗: {e}")


if __name__ == "__main__":
    output_name = "merged.pdf"
    merge_pdfs(output_name)
