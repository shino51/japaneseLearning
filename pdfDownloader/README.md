# PDF 連番ダウンローダー

指定したURLパターンで連番のPDFを一括ダウンロードするスクリプト  
存在しない番号は自動で飛ばして、存在する分だけキレイに保存します！

## 使い方
ターミナルで以下を実行
```bash
pip install requests tqdm
```
3. スクリプトを開いて「設定ここから」の部分を自分の欲しいものに書き換える  
4. 実行！
```bash
python download_sequential_pdf.py
```

## 設定例

| 欲しいファイル                | base_url                              | padding | start_num | end_num |
|------------------------------|---------------------------------------|---------|-----------|---------|
| meiro001.pdf ～ meiro043.pdf | http://meiro.moo.jp/meiro/meiro       | 3       | 1         | 43      |
| book01.pdf ～ book999.pdf    | https://example.com/book/book         | 2       | 1         | 999     |
| page1.pdf ～ page500.pdf     | https://site.com/pages/page           | 1       | 1         | 500     |

## 特徴

- 存在しない番号は自動スキップ
- すでにダウンロード済みは飛ばす（再実行が一瞬）
- 進捗バーで見やすい
- outputフォルダ自動作成

## 保存される場所

```text
output/
├── meiro001.pdf
├── meiro002.pdf
├── meiro004.pdf   ← 003はなかったので抜けてる
└── meiro043.pdf
```

これで全部一気にゲットできます！  
迷路・過去問・教科書・同人誌… 連番PDFならなんでもOK！

楽しんでね～！