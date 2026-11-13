# 日本語版の編集（2026-11-13更新）

**本文の正本は `classics/hongloumeng/ja/ch001.html` ～ `ch080.html` です。**
各ファイルの `<article>` と `</article>` の間を直接編集します。一段落を一行に整えています。散文は `<p class="prose">…</p>`、詩は `<p class="verse">…</p>` です。HTML内の `&`、`<` は必要に応じて `&amp;`、`&lt;` と書きます。

## ふだんの手順

1. 該当回のHTML本文を編集して保存します。JSONの変更、ハッシュの更新、翻訳原稿との同期は不要です。
2. `python3 -B scripts/build_hongloumeng_reading_japanese.py --check` で章・リンク・未訳マーカーを確認します。旧buildコマンドも、引数なしで実行しても**検査だけ**で、HTMLを書き換えません。
3. 回目・見出し・説明文を変えたときの検索への反映は `python3 -B scripts/build_search_index.py`。必要なら `python3 -B scripts/build_search_index.py --check` で確認します。検索は本文全文検索ではなく、回目・見出し・説明文などが対象です。ローカル生成と公開は別です。pushは所有者が行います。

文字サイズ、CSS、前後の回、四言語リンクは現状のままです。共通の見た目は同じフォルダーの `reader.css`、操作は `reader.js` を編集します。文章を変更するためにPythonを編集する必要はありません。章題を変えた場合だけ、その回の見出し・titleと `index.html` の回目も合わせてください。

未訳の11マーカーは変更していません。作者が補訳するまでは `<mark id="CH…">【日訳未完 CH…】</mark>` と告知を残してください。補訳して未訳数が変わる際は、その回の告知リンク、目次の未完表示、版説明、各ページの未訳件数を含むdescription、および作品入口の件数も合わせます。構造検査は文学的な完訳認定ではありません。

## 保存している履歴

このディレクトリのJSON原稿、原文対照、審読・進捗・placeholder-index、private-reviewは移行時点の履歴です。変更せず保存し、現在のHTMLと逐字同期しません。旧日訳pipelineとprivate-review生成は歴史的原稿の閲覧用で、現行サイトの公開条件ではありません。古いJSONから公開HTMLを再生成しないでください。以前の生成コードはgit履歴にあります。

簡体字・繁体字・英語の編集方式は変更していません。

---

## 旧作業記録（以下の手順は現行サイトの編集には使用しない）

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

## 検証方式の変更（2026-11-13）

ハッシュで固定した検証チェーン（B10から日本語ナビゲーションまでの各バインディング層）は、所有者の判断で廃止しました。各記録は `data/hongloumeng/first80-english/` に履歴としてそのまま残し、再生しません（`binding-chain-retirement.json`）。現在は今のファイルだけを検査します：`python3 -B -m unittest discover -s scripts -p test_hongloumeng_current_state.py`。

未訳箇所を補う手順：

1. 該当回の原稿に訳文を入れる。全箇所を補った回は `chNNN.partial.json` を `chNNN.draft.json`（区画ごとの `sourceText` と `text`）に置き換え、`python3 -B scripts/hongloumeng_japanese_pipeline.py --start 1 --end 80 --allow-partial` で確認する。
2. `scripts/build_hongloumeng_reading_japanese.py` の `PARTIAL` を更新する。告知文、版の説明、可用性検査の件数はここから決まる。`scripts/build_hongloumeng_hub.py` の件数表記（「11か所」「5回共11处」など）と、関連テストの期待値も合わせる。
3. `python3 -B scripts/hongloumeng_partial_private.py`（未完の回だけを自動で対象にする）と `python3 -B scripts/build_hongloumeng_reading_japanese.py` を実行し、macOS で `scripts/refresh_hongloumeng_reading_discovery.py --write`（入口ページ・検索・sitemap）を実行する。
4. 新しい審読記録を `reviews/` に加える。既存の審読記録は書き換えない。
