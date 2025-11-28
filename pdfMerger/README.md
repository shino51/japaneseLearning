# PDF 一括マージツール（暗号化PDFも自動解除対応）

複数のPDFを1つにまとめるPythonスクリプトです。  
暗号化されているPDFも、パスワードなし or よくあるパスワードなら自動で解除してマージできます。

## 必要な環境
- Python 3.9 以上（3.11〜3.13推奨）

## セットアップ手順（Windows/Mac/Linux共通）

1. 仮想環境を作成・起動

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

2. ライブラリインストール

```bash
pip install --upgrade pip
pip install -r ../requirements.txt
```

3`merge_pdf.py` の一番下を自分の環境に書き換えて実行

```bash
python merge_pdf.py
```