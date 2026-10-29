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
