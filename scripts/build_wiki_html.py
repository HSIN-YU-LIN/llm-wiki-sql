# -*- coding: utf-8 -*-
"""把 wiki/*.md 與 sources/INDEX.md 組成單一可瀏覽的 HTML Wiki。"""
import os, re, json, html, pathlib, datetime
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
OUT  = ROOT / "build" / "wiki.html"

CATS = {"A": "關聯式模型與 SQL 語意", "B": "儲存與索引",
        "C": "查詢執行與最佳化器", "D": "引擎實作差異"}

# ---- 來源表：從 sources/INDEX.md 解析 S編號 → (標題, 網址) ----
src_md = (ROOT / "sources" / "INDEX.md").read_text(encoding="utf-8")
SOURCES = {}
for m in re.finditer(r"\|\s*(S\d+)\s*\|\s*([^|]+?)\s*\|\s*(https?://\S+?)\s*\|", src_md):
    SOURCES[m.group(1)] = (m.group(2).strip(), m.group(3).strip())

md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])

entries = []
for fn in sorted(os.listdir(WIKI)):
    if not fn.endswith(".md"):
        continue
    code = fn.split("-")[0]
    raw = (WIKI / fn).read_text(encoding="utf-8")
    title = raw.splitlines()[0].lstrip("# ").strip()
    body_md = "\n".join(raw.splitlines()[1:])
    md.reset()
    body = md.convert(body_md)
    # [S1] → 可點擊來源標記
    def cite(mm):
        s = mm.group(1)
        if s not in SOURCES:
            return mm.group(0)
        t, u = SOURCES[s]
        return (f'<a class="cite" href="{html.escape(u)}" target="_blank" rel="noopener" '
                f'title="{html.escape(t)}">{s}</a>')
    body = re.sub(r"\[(S\d+)\]", cite, body)
    # 「寫稿注意 / 覆蓋缺口」區塊上色
    body = body.replace("<blockquote>", '<blockquote class="warn">')
    entries.append({"code": code, "title": title, "html": body,
                    "cites": len(re.findall(r'class="cite"', body))})

nav = []
for c, label in CATS.items():
    items = [e for e in entries if e["code"].startswith(c)]
    nav.append(f'<div class="navgrp"><div class="navcat">{c} · {html.escape(label)}</div>' +
               "".join(f'<a href="#{e["code"]}" data-code="{e["code"]}">'
                       f'<b>{e["code"]}</b> {html.escape(e["title"].split("—")[-1].strip())}</a>'
                       for e in items) + "</div>")

arts = "".join(
    f'<article id="{e["code"]}"><h2>{html.escape(e["title"])}'
    f'<span class="badge">{e["cites"]} 處引註</span></h2>{e["html"]}</article>'
    for e in entries)

srows = "".join(
    f'<tr><td>{s}</td><td>{html.escape(t)}</td>'
    f'<td><a href="{html.escape(u)}" target="_blank" rel="noopener">開啟</a></td></tr>'
    for s, (t, u) in sorted(SOURCES.items(), key=lambda kv: int(kv[0][1:])))

built = datetime.datetime.now().strftime("%Y-%m-%d")
doc = f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SQL 查詢執行與效能 — LLM Wiki</title>
<style>
:root{{--paper:#faf8f4;--ink:#1f1d1a;--ink2:#55514a;--ink3:#8a847a;--line:#e2ddd3;
--teal:#0f6e56;--teal-bg:#e4f2ec;--amber:#8a5a0b;--amber-bg:#fbf0dc;--code:#f2efe8;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--paper);color:var(--ink);font:16px/1.75 system-ui,"Noto Sans TC",sans-serif;
display:grid;grid-template-columns:290px 1fr;min-height:100vh}}
nav{{border-right:1px solid var(--line);padding:26px 18px;position:sticky;top:0;height:100vh;overflow:auto}}
nav h1{{font-size:17px;line-height:1.4;margin-bottom:4px}}
nav .sub{{font-size:12.5px;color:var(--ink3);margin-bottom:20px}}
.navgrp{{margin-bottom:16px}}
.navcat{{font-size:11.5px;letter-spacing:.06em;color:var(--ink3);margin-bottom:5px}}
nav a{{display:block;padding:4px 8px;border-radius:5px;color:var(--ink2);text-decoration:none;font-size:13.5px}}
nav a b{{color:var(--teal);font-weight:600;margin-right:5px}}
nav a:hover{{background:var(--teal-bg)}}
nav a.on{{background:var(--teal-bg);color:var(--ink)}}
main{{padding:44px 54px;max-width:900px}}
.intro{{border:1px solid var(--line);background:#fff;border-radius:10px;padding:20px 24px;margin-bottom:40px}}
.intro h2{{font-size:19px;margin-bottom:10px;border:0;padding:0}}
.intro p{{font-size:14.5px;color:var(--ink2);margin-bottom:8px}}
article{{margin-bottom:52px;scroll-margin-top:20px}}
article h2{{font-size:21px;border-bottom:2px solid var(--teal);padding-bottom:7px;margin-bottom:16px}}
article h3{{font-size:16px;margin:22px 0 8px;color:var(--teal)}}
article p,article li{{font-size:14.8px;color:var(--ink2)}}
article ul,article ol{{margin:8px 0 8px 22px}}
article li{{margin-bottom:4px}}
code{{background:var(--code);padding:1px 5px;border-radius:3px;font:13.5px ui-monospace,monospace;color:#7a2d2d}}
pre{{background:var(--code);padding:12px 14px;border-radius:7px;overflow:auto;margin:10px 0}}
pre code{{background:0;padding:0;color:var(--ink)}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.8px}}
th,td{{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}}
th{{background:var(--teal-bg)}}
blockquote.warn{{background:var(--amber-bg);border-left:3px solid var(--amber);
padding:11px 15px;margin:14px 0;border-radius:0 6px 6px 0}}
blockquote.warn p{{color:var(--amber);font-size:14px}}
.badge{{float:right;font-size:11.5px;color:var(--ink3);font-weight:400;background:var(--code);
padding:2px 9px;border-radius:11px;margin-top:3px}}
a.cite{{display:inline-block;font-size:11px;background:var(--teal-bg);color:var(--teal);
padding:0 5px;border-radius:3px;text-decoration:none;vertical-align:1px;font-weight:600}}
a.cite:hover{{background:var(--teal);color:#fff}}
#src td:first-child{{color:var(--teal);font-weight:600;white-space:nowrap}}
@media(max-width:860px){{body{{grid-template-columns:1fr}}nav{{position:static;height:auto}}main{{padding:28px 20px}}}}
</style></head><body>
<nav><h1>SQL 查詢執行與效能</h1><div class="sub">LLM Wiki · 19 條條目 · 17 篇來源<br>建立於 {built}</div>
{''.join(nav)}
<div class="navgrp"><div class="navcat">附錄</div><a href="#sources"><b>S</b> 來源索引</a></div>
</nav>
<main>
<div class="intro"><h2>關於這份 Wiki</h2>
<p>主題為 <b>SQL 查詢的執行與效能</b>：從關聯式模型與 SQL 語意出發，到索引結構、查詢最佳化器，
以及三家資料庫引擎的實作差異。</p>
<p>建立方式為「先討論、後生成」——先敲定 A～D 四類共 19 條條目的架構與各條目職責，再依架構抓取資料。
全部 17 篇來源均為一手來源：PostgreSQL 18 / MySQL 8.0 / SQLite 官方文件，以及 Use The Index, Luke。</p>
<p>條目中每一項陳述後方的綠色標記（如 <a class="cite" href="#sources">S1</a>）是來源引註，可點擊開啟原文。
琥珀色區塊是 <b>寫稿注意</b>：標記「來源其實沒有說這件事」，供後續產製簡報時避免憑推測補寫。</p></div>
{arts}
<article id="sources"><h2>來源索引（17 篇）</h2>
<table id="src"><tr><th>編號</th><th>來源</th><th>連結</th></tr>{srows}</table></article>
</main>
<script>
var links=[].slice.call(document.querySelectorAll('nav a'));
var obs=new IntersectionObserver(function(es){{
  es.forEach(function(e){{ if(e.isIntersecting){{
    links.forEach(function(a){{a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id)}});
  }}}});
}},{{rootMargin:'-10% 0px -80% 0px'}});
document.querySelectorAll('article').forEach(function(a){{obs.observe(a)}});
</script></body></html>"""
OUT.write_text(doc, encoding="utf-8")
print("entries:", len(entries), "| sources:", len(SOURCES), "| bytes:", OUT.stat().st_size)
print("cites per entry:", {e["code"]: e["cites"] for e in entries})
