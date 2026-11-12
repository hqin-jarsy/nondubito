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
python3 -B scripts/hongloumeng_japanese_pipeline.py --start 1 --end 10 --allow-partial
```

`--allow-partial` は部分稿の範囲を確認する指定であり、完全版への昇格ではありません。完全な回だけを校閲HTMLへ出すときは `--render-private` を指定します。中国語の源文が変わった場合は、その回の源ハッシュと対応文を確認し直す必要があります。

五回ごとに内容と文体を振り返ってローカルでcommitします。pushは行いません。未完成部分、確認待ちの作者訳文、未実施の検査を、完了と表示しません。
