# 王珣《伯遠帖》 八語閱讀包

先開啟 READ.html，選擇語言。每種語言有完整 Markdown 與 HTML；八種版本均保留整封古文、完整現代語譯文、四個相鄰列細節與可選附讀。16另有內嵌本文總覽，15全幅由文內連結開啟。

Languages: 简体中文、繁體中文、English、Deutsch、Français、Español、日本語、한국어。

## 檔案

- 16_boyuan_*.md / .html：八語完整文章
- images/：館方真實影像的五個檔案，含總覽與四個局部
- SOURCES.md：作品、歷史、釋文與理論來源
- IMAGE_NOTES.md / IMAGE_MANIFEST.json：圖片來源、座標、加工及許可狀態
- MANIFEST.json / SHA256SUMS.txt：檔案清單與完整性校驗
- build.py / requirements.txt：由MD重建HTML、導航、清單和校驗值

## 重建

Python 3.9以上，安裝 requirements.txt 中的 Markdown 後執行 python build.py。靜態HTML僅使用本地圖片，無外部字型、腳本或追蹤。

## 檢驗範圍

簡體稿已逐篇編輯並對圖；繁體已逐段檢查多義字及語義，不把自動轉字當成完成。六種外語為整篇譯文，非摘要；保留字形、相鄰字、列位與史實不確定性。圖片逐張實際開啟。HTML連結、圖片路徑、語言導航與折疊說明已完成靜態檢查。未完成實際瀏覽器渲染檢查，不宣稱逐屏視覺或行動端版面已核驗。語審與檢查範圍見QA.md。

圖片未取得另行出版許可，公開可看不等於授權；對外再版前須確認。這是數位影像細讀，不是原件現場鑑定。

Open READ.html to select a complete language edition. Images are real museum photographs, cropped without reconstruction. Separate publication permission has not been obtained. See IMAGE_NOTES.md for exact provenance and limits.
