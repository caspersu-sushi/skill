---
name: "pdf-shelf-viewer"
description: "Use when the user uploads PDF, PPT/PPTX or Word files and wants to browse them, switch between them, or see them in a side panel or viewer with a file list."
---

# PDF shelf viewer

Turn the files the user uploaded into one published artifact page: a file list on the left (grouped, with page counts), the chosen PDF rendered on the right with pdf.js, page jump and zoom. On phones the list becomes a dropdown. Reply to the user in Traditional Chinese (繁體中文) unless they ask for English.

Do not ask questions first. Take the best guess for titles and groups, build, publish, and say in one or two sentences what is on the shelf.

## Steps

Work in a folder in the scratchpad, called `V` below, with a subfolder `V/pdf`.

1. **Find the files.** Uploaded files are under `/mnt/user-data/attachments/<id>/` or `/mnt/user-data/uploads/`. Uploaded names often lose their Chinese characters (they look like `090950b8-_______v20260930.pdf`), so never use the file name as the title.

2. **Convert non-PDF files.** For `.ppt .pptx .doc .docx .odp`: copy to a temp folder with a plain ASCII name, then `soffice --headless --convert-to pdf --outdir <out> <files>` (allow up to 5 minutes). Check page counts with `pdfinfo`.

3. **Name and group.** Copy every PDF to `V/pdf/` with an ASCII, ordered name (`dsd-1-ic-flow.pdf`, `cpp-18.pdf`). Get a real title from the first page: `pdftotext -f 1 -l 1 -layout file.pdf - | grep -v '^\s*$' | head -6`. Skip school or course header lines and use the line that names the topic (for slides converted from PPT, the extracted first-slide text works too). Use the course name as `group` when several files share it. Order files by chapter or lesson number.

4. **Write `V/manifest.json`:**
```json
{"title": "我的課程講義", "files": [
  {"path": "pdf/dsd-1-ic-flow.pdf", "title": "IC 設計流程介紹", "group": "數位系統設計實習"}
]}
```
The `title` is the page name: a short specific name such as the course name, or `我的課程講義` when files span several courses.

5. **Write the build script and template below, then build:** `python3 -I build_viewer.py V/manifest.json viewer_template.html V/index.html`. Keep the scripts outside `V`.

6. **Publish** with the Artifact tool: `file_path` = `V/index.html`, `icon` = `book`, a one-sentence `description`, and `files` mapping each published path to its file, e.g. `{"pdf/cpp-18.pdf": "V/pdf/cpp-18.pdf"}` (absolute source paths). Limits: 15MB per PDF, 64MB per publish; for more, publish again to the same `url` with the remaining PDFs (files already published are kept). If one PDF is over 15MB, compress it first: `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -o out.pdf in.pdf`.

7. **Reply** in one or two sentences: what is on the shelf, and that the page is in their artifacts so it can be reopened from any chat. Do not paste the URL.

## Adding files to an existing shelf

If the user says to add files to the shelf they already have, find it with Artifact `action: "list"` (title like the earlier one), then `action: "read"` its `url`. The file list is the `var FILES = [...]` array in the page. Rebuild the manifest from that list plus the new files (keep the old `path` values), build `index.html` again, and publish with that `url`, passing only the new PDFs in `files`; the old PDFs stay published.

## build_viewer.py

```python
"""Build a PDF shelf viewer page. Usage: python3 build_viewer.py manifest.json template.html out.html
manifest: {"title": "...", "files": [{"path": "pdf/a.pdf", "title": "...", "group": "..."}]}
Paths are relative to out.html's folder; page counts are filled in with pdfinfo."""
import json, os, subprocess, sys
man = json.load(open(sys.argv[1], encoding="utf-8"))
tpl = open(sys.argv[2], encoding="utf-8").read()
out = sys.argv[3]
root = os.path.dirname(os.path.abspath(out))
for f in man["files"]:
    if f.get("pages"):
        continue
    info = subprocess.run(["pdfinfo", os.path.join(root, f["path"])], capture_output=True, text=True).stdout
    f["pages"] = next((int(l.split()[-1]) for l in info.splitlines() if l.startswith("Pages:")), None)
data = json.dumps(man["files"], ensure_ascii=False).replace("</", "<\\/")
title = man["title"].replace("&", "&amp;").replace("<", "&lt;")
open(out, "w", encoding="utf-8").write(tpl.replace("__TITLE__", title).replace("__FILES__", data))
print(out, len(man["files"]), "files")
```

When adding to an existing shelf whose old PDFs are not on disk, keep each old entry's `pages` value in the manifest; the script skips entries that already have one.

## viewer_template.html

Write this file exactly. `__TITLE__` and `__FILES__` are filled in by the script.

```html
<title>__TITLE__</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap">
<style>
/* Layout: reading-room shelf. File list on the left, the open PDF fills the rest; on phones the list becomes a picker on top. */
:root{
  --bg:#eceeea; --shelf:#f7f8f5; --paper:#ffffff; --fg:#1f2724; --muted:#64706b; --line:#d5dad5;
  --accent:#2c6e5a; --accent-fg:#ffffff; --accent-soft:#dbeae3;
  --font:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121615; --shelf:#1a201e; --paper:#ffffff; --fg:#e3e9e6; --muted:#97a49f; --line:#2c3532;
  --accent:#6cc4a6; --accent-fg:#0d1513; --accent-soft:#223630; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121615; --shelf:#1a201e; --paper:#ffffff; --fg:#e3e9e6; --muted:#97a49f; --line:#2c3532;
  --accent:#6cc4a6; --accent-fg:#0d1513; --accent-soft:#223630; color-scheme:dark}
html,body{height:100%}
body{background:var(--bg);color:var(--fg);font-family:var(--font);font-size:14px;line-height:1.5;overflow:hidden}
.app{display:grid;grid-template-columns:260px minmax(0,1fr);grid-template-rows:minmax(0,1fr);height:100%;overflow:hidden}
.shelf{background:var(--shelf);border-right:1px solid var(--line);overflow-y:auto;padding-block:14px;
  padding-left:max(12px,env(safe-area-inset-left,0px));padding-right:12px;display:flex;flex-direction:column;gap:14px}
.shelf h1{font-size:15px;margin:0 4px;text-wrap:balance}
.group{display:flex;flex-direction:column;gap:2px}
.group h2{font-size:11px;font-weight:500;letter-spacing:.08em;color:var(--muted);margin:0 8px 4px;text-transform:uppercase}
.file{display:flex;justify-content:space-between;gap:8px;align-items:baseline;text-align:left;font:inherit;color:var(--fg);
  background:none;border:0;border-radius:6px;padding:7px 8px;cursor:pointer}
.file:hover{background:var(--accent-soft)}
.file[aria-current="true"]{background:var(--accent);color:var(--accent-fg)}
.file span{min-width:0;overflow-wrap:anywhere}
.file small{flex:none;font-size:11px;opacity:.7;font-variant-numeric:tabular-nums}
.main{display:flex;flex-direction:column;min-width:0;min-height:0;overflow:hidden}
.bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding-block:8px;padding-left:16px;
  padding-right:max(16px,env(safe-area-inset-right,0px));border-bottom:1px solid var(--line);background:var(--shelf)}
.bar .name{font-weight:700;flex:1 1 200px;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.picker{display:none;flex:1 1 100%;font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--paper);color:#1f2724}
.btn{font:inherit;min-width:34px;padding:4px 10px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);cursor:pointer}
.btn:hover{border-color:var(--accent)}
.pg{display:flex;align-items:center;gap:4px;color:var(--muted);font-variant-numeric:tabular-nums}
.pg input{width:4.5ch;font:inherit;text-align:right;padding:3px 4px;border:1px solid var(--line);border-radius:5px;background:var(--bg);color:var(--fg)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.pages{flex:1;min-height:0;overflow:auto;position:relative;padding:16px;display:flex;flex-direction:column;align-items:center;gap:12px}
.page{background:var(--paper);box-shadow:0 1px 3px rgba(0,0,0,.18);position:relative;max-width:100%;flex:none}
.page canvas{display:block;width:100%;height:100%}
.page .no{position:absolute;right:8px;bottom:6px;font-size:11px;color:#8a938f}
.msg{color:var(--muted);margin-top:40px;text-align:center}
@media (max-width:720px){
  .app{grid-template-columns:1fr}
  .shelf{display:none}
  .picker{display:block}
  .bar .name{display:none}
  .bar{padding-left:max(16px,env(safe-area-inset-left,0px))}
  .pages{padding:10px}
}
</style>
<div class="app">
  <nav class="shelf" id="shelf" aria-label="檔案"></nav>
  <section class="main">
    <div class="bar">
      <select class="picker" id="picker" aria-label="選擇檔案"></select>
      <div class="name" id="name"></div>
      <div class="pg"><input id="pageInput" type="text" inputmode="numeric" aria-label="頁碼"><span id="pageTotal"></span></div>
      <button class="btn" id="zoomOut" aria-label="縮小">−</button>
      <button class="btn" id="fit">符合寬度</button>
      <button class="btn" id="zoomIn" aria-label="放大">+</button>
    </div>
    <div class="pages" id="pages"><p class="msg">載入中…</p></div>
  </section>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js"></script>
<script>
var FILES = __FILES__;
var lib = window.pdfjsLib;
if (lib) lib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
var $ = function(id){ return document.getElementById(id) };
var baseW = 720, cache = {}, doc = null, cur = null, zoom = 0, observer = null, token = 0, pageBoxes = [];
var KEY = "pdf-shelf:" + document.title;
function load(){ try { return JSON.parse(localStorage.getItem(KEY) || "{}") } catch(e){ return {} } }
function save(o){ try { localStorage.setItem(KEY, JSON.stringify(o)) } catch(e){} }
var saved = load();
function esc(t){ return String(t).replace(/[&<>"]/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c] }) }

function buildShelf(){
  var groups = [];
  FILES.forEach(function(f, i){
    var g = groups.find(function(x){ return x.name === (f.group || "") });
    if (!g) { g = { name: f.group || "", items: [] }; groups.push(g) }
    g.items.push(i);
  });
  $("shelf").innerHTML = "<h1>" + esc(document.title) + "</h1>" + groups.map(function(g){
    return '<div class="group">' + (g.name ? "<h2>" + esc(g.name) + "</h2>" : "") + g.items.map(function(i){
      var f = FILES[i];
      return '<button class="file" data-i="' + i + '"><span>' + esc(f.title) + "</span><small>" + (f.pages ? f.pages + " 頁" : "") + "</small></button>";
    }).join("") + "</div>";
  }).join("");
  $("picker").innerHTML = groups.map(function(g){
    var opts = g.items.map(function(i){ return '<option value="' + i + '">' + esc(FILES[i].title) + "</option>" }).join("");
    return g.name ? '<optgroup label="' + esc(g.name) + '">' + opts + "</optgroup>" : opts;
  }).join("");
}

function mark(i){
  document.querySelectorAll(".file").forEach(function(b){ b.setAttribute("aria-current", String(+b.dataset.i === i)) });
  $("picker").value = String(i);
  $("name").textContent = FILES[i].title;
}

function open(i, startPage){
  cur = i; mark(i);
  var my = ++token;
  $("pages").innerHTML = '<p class="msg">載入中…</p>';
  var p = cache[i] || (cache[i] = lib.getDocument({ url: FILES[i].path }).promise);
  p.then(function(d){
    if (my !== token) return;
    doc = d; layout(startPage || 1);
    save({ file: i, page: startPage || 1 });
  }).catch(function(err){
    delete cache[i];
    if (my === token) $("pages").innerHTML = '<p class="msg">這個檔案打不開:' + esc(err && err.message || err) + "</p>";
  });
}

function fitWidth(){ return Math.max(200, $("pages").clientWidth - (window.innerWidth <= 720 ? 20 : 32)) }

function layout(goTo){
  var my = token;
  doc.getPage(1).then(function(first){
    if (my !== token) return;
    var base = first.getViewport({ scale: 1 });
    baseW = base.width;
    var width = zoom ? base.width * zoom : Math.min(fitWidth(), base.width * 2);
    var box = $("pages"); box.innerHTML = ""; pageBoxes = [];
    if (observer) observer.disconnect();
    observer = new IntersectionObserver(function(entries){
      entries.forEach(function(en){ if (en.isIntersecting) draw(+en.target.dataset.n, en.target) });
      updateCounter();
    }, { root: box, rootMargin: "600px 0px" });
    for (var n = 1; n <= doc.numPages; n++){
      var div = document.createElement("div");
      div.className = "page"; div.dataset.n = n;
      div.style.width = width + "px";
      div.style.aspectRatio = base.width + " / " + base.height;
      div.innerHTML = '<span class="no">' + n + "</span>";
      box.appendChild(div); pageBoxes.push(div); observer.observe(div);
    }
    $("pageTotal").textContent = "/ " + doc.numPages;
    if (goTo > 1 && pageBoxes[goTo - 1]) box.scrollTop = pageBoxes[goTo - 1].offsetTop - 16;
    else box.scrollTop = 0;
    updateCounter();
  });
}

function draw(n, div){
  if (div.dataset.done) return;
  div.dataset.done = "1";
  var my = token;
  doc.getPage(n).then(function(page){
    if (my !== token) return;
    var base = page.getViewport({ scale: 1 });
    var cssW = div.clientWidth || base.width;
    var ratio = Math.min(window.devicePixelRatio || 1, 2);
    var vp = page.getViewport({ scale: (cssW / base.width) * ratio });
    var c = document.createElement("canvas");
    c.width = Math.floor(vp.width); c.height = Math.floor(vp.height);
    div.insertBefore(c, div.firstChild);
    return page.render({ canvasContext: c.getContext("2d"), viewport: vp }).promise;
  }).catch(function(){ delete div.dataset.done });
}

function currentPage(){
  var box = $("pages"), top = box.scrollTop + box.clientHeight * 0.3, n = 1;
  for (var k = 0; k < pageBoxes.length; k++){ if (pageBoxes[k].offsetTop <= top) n = k + 1; else break }
  return n;
}
var saveTimer;
function updateCounter(){
  if (!doc) return;
  var n = currentPage();
  if (document.activeElement !== $("pageInput")) $("pageInput").value = n;
  clearTimeout(saveTimer);
  saveTimer = setTimeout(function(){ save({ file: cur, page: n }) }, 400);
}

$("shelf").addEventListener("click", function(e){ var b = e.target.closest(".file"); if (b) open(+b.dataset.i, 1) });
$("picker").addEventListener("change", function(){ open(+this.value, 1) });
$("pages").addEventListener("scroll", updateCounter, { passive: true });
$("pageInput").addEventListener("change", function(){
  var n = Math.max(1, Math.min(doc ? doc.numPages : 1, parseInt(this.value, 10) || 1));
  if (pageBoxes[n - 1]) $("pages").scrollTop = pageBoxes[n - 1].offsetTop - 16;
});
function setZoom(z){
  if (!doc) return;
  var n = currentPage();
  zoom = z; layout(n);
}
function nowScale(){
  var w = pageBoxes[0] ? pageBoxes[0].clientWidth : 800;
  return w / baseW;
}
$("zoomIn").onclick = function(){ setZoom(Math.min(4, (zoom || nowScale()) * 1.2)) };
$("zoomOut").onclick = function(){ setZoom(Math.max(0.3, (zoom || nowScale()) / 1.2)) };
$("fit").onclick = function(){ setZoom(0) };
var rt;
window.addEventListener("resize", function(){ if (!zoom && doc){ clearTimeout(rt); rt = setTimeout(function(){ layout(currentPage()) }, 250) } });

buildShelf();
if (!lib) { $("pages").innerHTML = '<p class="msg">PDF 元件載入失敗,請重新整理頁面。</p>' }
else if (!FILES.length) { $("pages").innerHTML = '<p class="msg">還沒有檔案。</p>' }
else {
  var start = (saved.file >= 0 && saved.file < FILES.length) ? saved.file : 0;
  open(start, saved.file === start ? saved.page : 1);
}
</script>
```

## Notes

- The page loads pdf.js and its worker as plain scripts from cdnjs; the worker then runs on the main thread, which the artifact frame allows. Do not change it to a separate worker URL.
- Only pages near the screen are drawn, so long files stay fast.
- The page remembers the last file and page per viewer in browser storage; that is a convenience only.