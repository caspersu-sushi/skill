# skill

我的 Claude skills。

## pdf-shelf-viewer

上傳 PDF、PPT 或 Word 檔後,建立一個講義瀏覽頁面:左邊列出檔案(分組並標示頁數),右邊用原本的版面顯示選到的 PDF,可以跳頁和縮放。

- `SKILL.md`:skill 本體,Claude 依照它執行
- `viewer_template.html`:瀏覽頁面的範本
- `build_viewer.py`:依照 manifest 產生頁面的腳本

SKILL.md 已經內含範本和腳本,另外兩個檔案方便直接查看或修改。
