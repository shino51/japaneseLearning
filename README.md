# japaneseLearning
子どもの日本語教育に関する事を便利に使うツール集

# 便利なLink集
[学習プリント.com](https://xn--fdk3a7ctb5192box5b.com/yo/)

[めいろやさん](http://meiro.moo.jp/)

[Honda Kids](https://www.honda.co.jp/kids/okeiko/)

[がんプリ](https://gampuri.net/gampuri_kokugo)

# PDF吸い取り＋結合マシーン

**「ページに貼ってあるPDF全部」→ 1クリックで自動ダウンロード → 1つの完璧なPDFに結合 → ダウンロードフォルダに保存！**

めっちゃ便利な絵本・同人誌・問題集・教科書・資料を、**たった10秒で1つのPDFにまとめる**最強ツール！！

https://your-username-pdf-tool.streamlit.app

## できること（全部自動！）

- ページ内のPDFリンクを全部検出
- 一括ダウンロード（抜けなし）
- 順番通りに結合
- **同じ名前があっても上書きしない！Chromeと同じ「(1)」「(2)」自動連番**
- ローカル実行なら自動で **「ダウンロード」フォルダ** に保存
- フォルダ変えたい？ → チェックひとつで選択可能
- ブラウザで動くから友達にも即共有できる！

## 使い方（超簡単）

1. 上のURLにアクセス（またはローカルで `streamlit run app.py`）
2. PDFが載ってるページのURLをペースト  
   例：`https://xn--fdk3a7ctb5192box5b.com/yo/oekaki/ewonazoru_step1.html`
3. 完成PDFの名前を入力（例：`えほんざうるす.pdf`）
4. **「全PDFダウンロード → 結合 → 保存！！」** をポチッ
5. 自動で保存されるか、ダウンロードボタンで即ゲット！

→ 完成！！

## ローカルで動かしたい人向け

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install streamlit requests beautifulsoup4 PyPDF2  # または君のmergeで使ってるライブラリ
streamlit run app.py
```

## クレジット
Made with pure vibe coding energy by Shino