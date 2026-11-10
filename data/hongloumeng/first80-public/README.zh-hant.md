# 前八十回繁體字形版

本版以同目錄已定稿的 `reading.zh.json` 為唯一正文輸入，僅轉換字形，不改詞句、標點、分段或詩文行序。簡體版與繁體版均為 80 回、4,394 個展示塊、586,205 個正文 Unicode 碼點；303 組詩文版式沿用原版。

## 重建

在倉庫根目錄執行：

```sh
python3 -B scripts/build_hongloumeng_first80_traditional.py
python3 -B scripts/build_hongloumeng_first80_traditional.py --check
python3 -B scripts/test_hongloumeng_first80_traditional.py
```

重建僅需 Python 標準庫，不需網絡、字形轉換服務或特定作業系統。建置程式核對簡體輸入、簡體 manifest 及正文的固定 SHA-256，拒絕在底本已變動時套用舊規則。

## 資料格式

- `conversion.zh-hant.json`：此版專用的固定字形映射及按語境選字的例外。不是可套用到其他文本的通用轉換詞典。
- `reading.zh-hant.json`：與簡體閱讀資料同一結構，語言標記為 `zh-Hant`。
- `manifest.zh-hant.json`：逐回正文雜湊、字數、展示塊及版式統計。字體與 renderer 資訊沿用簡體版。

映射表的鍵和值都是單一 Unicode 碼點。例外中的 `chapter` 為回次，`block` 為從零開始的展示塊序號；回目使用 `"title"`，全書標題使用回次 0。`offset` 是該字串內從零開始的 Unicode 碼點位置，**不是 UTF-16 code unit 或 UTF-8 位元組位置**。每個例外包含原字、目標字及完整來源字串的 SHA-256，防止位置錯配。

## 字形原則

沿用既有繁體閱讀版的「裡」「著」等字形；里程仍用「里」，人物姓氏和稱謂按語境保留。區分發／髮、干／乾／幹、只／隻、面／麵、余／餘、系／係／繫、鐘／鍾、采／採、准／準等。原文固有的異體不作無關的詞形整理，不替換地域詞彙，不新增注釋或版本標籤。

每個字形選擇都保持一個碼點對應一個碼點；非漢字字元、罕見補充平面字元及全部版式欄位保持不變。結構測試驗證內容沒有增刪，語境回歸測試另行檢查易混字，二者不可互相替代。

## 本地閱讀預覽

在倉庫根目錄執行以下命令。輸出僅供本機預覽，頁面設有 noindex，不作公開發布。

```sh
preview=$(mktemp -d "${TMPDIR:-/tmp}/hlm-reader.XXXXXX")
python3 -B scripts/build_hongloumeng_reading.py --mode draft --bilingual --output "$preview"
python3 -B scripts/build_hongloumeng_reading_traditional.py --mode draft --output "$preview/zh-hant"
python3 -B scripts/test_hongloumeng_reading_traditional.py
```

## 已獲批准的本地雙語重建

以下命令只重建本地檔案，不會自動 push。呼叫者須先取得與目前輸入雜湊綁定的批准檔案，再以環境變數 `SIMPLIFIED_APPROVAL`、`TRADITIONAL_APPROVAL` 指定其位置；此處不建立或提供批准內容。

```sh
python3 -B scripts/build_hongloumeng_reading_traditional.py --mode release --output classics/hongloumeng/zh-hant --release-approval "$TRADITIONAL_APPROVAL"
python3 -B scripts/build_hongloumeng_reading.py --mode release --bilingual --output classics/hongloumeng --release-approval "$SIMPLIFIED_APPROVAL" --traditional-release-approval "$TRADITIONAL_APPROVAL"
```

正式雙語重建必須明確啟用 `--bilingual`。未啟用時，簡體 renderer 保持原有單語輸出契約，不會自動加入繁體導覽。
