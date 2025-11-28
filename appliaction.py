from pdfDownloader.download_pdfs_from_page import download_pdfs_from_page
from pdfMerger.merge_pdf import merge_pdfs


if __name__ == "__main__":
    # ダウンロードしてpdf を全てマージする
    target_url = "https://xn--fdk3a7ctb5192box5b.com/yo/unpitsu/senwohiku1_step1.html"

    output_dir = "../pdfMerger/input"
    download_pdfs_from_page(target_url, output_dir)
    output_filename="merged.pdf"
    merge_pdfs(_output_filename=output_filename)
