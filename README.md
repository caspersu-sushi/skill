# skill

我的 Claude skills。

## pdf-shelf-viewer

上傳 PDF、PPT 或 Word 檔後,建立一個講義瀏覽頁面:左邊列出檔案(分組並標示頁數),右邊用原本的版面顯示選到的 PDF,可以跳頁和縮放。

**下載:** [pdf-shelf-viewer.zip](https://github.com/caspersu-sushi/skill/raw/main/dist/pdf-shelf-viewer.zip)(已打包好,可以直接上傳到 Claude)

### 安裝

1. 到 Claude 的 Settings → Capabilities,打開「Code execution and file creation」(新版叫「Create and edit files」)。
2. 下載上面的 `pdf-shelf-viewer.zip`,不用解壓縮。
3. 到 Customize → Skills,按「+」→「+ Create skill」→「Upload a skill」,選這個 zip。
4. 開一個新聊天,上傳 PDF 或 PPT,說「幫我做成講義瀏覽器」。

### 檔案

- `pdf-shelf-viewer/SKILL.md`:skill 本體,Claude 依照它執行
- `pdf-shelf-viewer/viewer_template.html`:瀏覽頁面的範本
- `pdf-shelf-viewer/build_viewer.py`:依照 manifest 產生頁面的腳本
- `dist/pdf-shelf-viewer.zip`:上面三個檔案打包好的版本

SKILL.md 已經內含範本和腳本,另外兩個檔案方便直接查看或修改。改了 skill 之後,記得重新打包 `dist/` 裡的 zip。
