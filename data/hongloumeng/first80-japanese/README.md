# 紅楼夢・前八十回 日語翻訳作業

中国語の現行読本からの独立翻訳。第81–85回の独立日訳の人物名と声口を継承します。既刊翻訳の文章は使用しません。

- `chapters/chNNN.draft.json`：全区画を収録した日訳原稿。構造上の完備と文学審読の完了は別です。
- `chapters/chNNN.partial.json`：作者が訳文を挿入する箇所が残る原稿。省略を完全版として扱いません。通常の叙述は可能な限り残します。
- `sourceSegments`：原文の文字位置で安全な訳文と作者挿入待ちを分けます。`start` は0始まり、`end` はその直前まで。待機箇所の原文を複写せず、ハッシュで位置を拘束します。
- `reviews/`：実際に読んだ範囲、具体的な訳文修正、未解決事項。
- `private-review/`：非公開の校閲用HTML。公開読書ページではありません。
- `guiyou-comparison-001-010.json`：癸酉本文との個別比較。候補と、作者が明示的に採用した変更を分けています。

確認コマンド：

```sh
python3 -B scripts/test_hongloumeng_japanese_pipeline.py
python3 -B scripts/hongloumeng_japanese_pipeline.py --start 1 --end 80 --allow-partial
```

`--allow-partial` は部分稿の範囲を確認する指定であり、完全版への昇格ではありません。完全な回だけを校閲HTMLへ出すときは `--render-private` を指定します。中国語の源文が変わった場合は、その回の源ハッシュと対応文を確認し直す必要があります。

五回ごとに内容と文体を振り返ってローカルでcommitします。pushは行いません。未完成部分、確認待ちの作者訳文、未実施の検査を、完了と表示しません。

## 未完成箇所の一意なプレースホルダー

`placeholder-index.json` は回番号・マーカー・原文内位置・ハッシュのみの索引です。原文本文は収録しません。第6回は CH006-P01〜P03、第9回は CH009-P01〜P02、第12回は CH012-P01、第65回は CH065-P01〜P04、第75回は CH075-P01 です。計11箇所が作者の手動補完待ちです。`【日訳未完 CH006-P01】` のような文字列で検索できます。

`private-review/ch006.partial.html`、`ch009.partial.html`、`ch012.partial.html`、`ch065.partial.html`、`ch075.partial.html` には既存の日訳と黄色のマーカーだけを表示します。作者が手動補完する位置の確認用です。HTML編集はJSON原稿へ自動反映されません。原稿の正本は `chapters/chNNN.partial.json` です。マーカーだけを消しても完成扱いにはなりません。

再生成：`python3 -B scripts/hongloumeng_partial_private.py`。検査：`python3 -B scripts/test_hongloumeng_partial_private.py`。この独立レンダラーは中国語原文ファイルを読み込まず、欠落した訳文を原文で埋めません。構造検査は原文照合・文学的審読ではなく、旧reviewやprogressを変更しません。非公開はローカル用途の意味で、HTMLのnoindexはアクセス制御ではありません。公開・pushは行っていません。

## サイトの日本語読書ページ

`classics/hongloumeng/ja/` は公開用の生成先です。ローカルのファイル生成とリモート公開は別の操作です。push は所有者が行います。75回の全文稿と5回の部分稿を区別し、11か所の未訳マーカーと版の説明を表示します。内部の校閲メモや中国語への自動フォールバックは表示しません。

生成：`python3 -B scripts/build_hongloumeng_reading_japanese.py`。
構造と表示の単体検査：`PYTHONPATH=scripts python3 -B -m unittest test_hongloumeng_reading_japanese`。
ブラウザー検査：`scripts/test_hongloumeng_reading_japanese_browser.cjs`。ローカルHTTPサーバーと隔離したPlaywright環境を使用します。

旧言語ページへの日本語リンクは `scripts/integrate_hongloumeng_japanese.py` の限定的で可逆な変換で挿入します。旧版の校閲記録を新しい全面審読の証拠に書き換えません。第80回から第81回へのリンクには、曹雪芹の原著と秦漢の独自続編の境界を明記します。

終審記録：`reviews/final-poetry-audit.json` は929の詩区画と127の本文候補の実読範囲を記録します。`reviews/final-names-style-audit.json` は人物名・親族呼称・残存する中国語呼称の対象別修正を記録します。いずれも全散文の新たな逐段再読を主張しません。
