# -*- coding: utf-8 -*-
"""G2 忠實度關卡（追溯性部分）
1. 每頁 data-wiki 宣告的條目都必須真實存在於 wiki/
2. 每頁 data-wiki 必須與 OUTLINE.md 的規劃一致
3. 標示「已實跑」的頁，必須在 verify/outputs.json 中有該頁的通過範例
4. Wiki 的三項「寫稿注意」禁區不得出現在簡報中
5. 引擎相依關鍵詞必須與引擎名同頁出現
"""
import re, json, os, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
html = (ROOT/"build/index.html").read_text(encoding="utf-8")
wiki_codes = {f.split("-")[0] for f in os.listdir(ROOT/"wiki") if f.endswith(".md")}
verified = json.load(open(ROOT/"verify/outputs.json", encoding="utf-8"))
ok_slides = {r["slide"] for r in verified if r["status"] == "PASS"}

slides = re.findall(r'<section class="slide[^"]*" data-wiki="([^"]*)">(.*?)</section>', html, re.S)

outline = (ROOT/"slides/OUTLINE.md").read_text(encoding="utf-8")
plan = {}
for line in outline.splitlines():
    m = re.match(r"\|\s*(\d+)\s*\|[^|]*\|[^|]*\|\s*([^|]*?)\s*\|", line)
    if m:
        plan[int(m.group(1))] = {c.strip() for c in m.group(2).split(",") if re.fullmatch(r"[A-D]\d", c.strip())}

BLACKLIST = [
    (r"所有輸入.{0,6}null.{0,12}回傳", "A6 禁區：所有輸入皆 null 時的結果"),
    (r"一列.{0,6}跨頁|列可以跨越.{0,4}頁", "B1 禁區：列是否跨頁"),
    (r"hash join.{0,20}(優於|比.{0,6}快)|merge join.{0,20}(優於|比.{0,6}快)", "C2 禁區：hash/merge 何時較優"),
]
ENGINE_WORDS = ["PostgreSQL", "MySQL", "SQLite"]

fails, rows = [], []
for n, (wk, body) in enumerate(slides, 1):
    declared = {c.strip() for c in wk.split(",") if c.strip()}
    reasons = []

    missing = declared - wiki_codes
    if missing:
        reasons.append("引用不存在的條目:" + ",".join(sorted(missing)))

    if n in plan and plan[n] and declared != plan[n]:
        reasons.append(f"與大綱不符(大綱{sorted(plan[n])} vs 實際{sorted(declared)})")

    claims_run = 'class="tag ver"' in body   # 以徽章判定，而非內文字串（修正 v1 的誤判）
    if claims_run and n not in ok_slides:
        reasons.append("宣稱已實跑，但 outputs.json 中無該頁通過範例")

    for pat, label in BLACKLIST:
        if re.search(pat, body, re.I):
            reasons.append("觸碰禁區:" + label)

    # 引擎相依關鍵詞
    txt = re.sub(r"<[^>]+>", " ", body)
    for kw in ["EXPLAIN", "collation", "COLLATE", "別名"]:
        if kw in txt and not any(e in txt for e in ENGINE_WORDS):
            reasons.append(f"提及「{kw}」但未標明引擎")
            break

    status = "PASS" if not reasons else "FAIL"
    rows.append((n, len(declared), "是" if claims_run else "-", status, "; ".join(reasons)))
    if reasons:
        fails.append(n)

print(f"{'頁':>3} {'條目數':>6} {'實跑':>4}  {'判定':<5} 原因")
print("-"*78)
for n, d, r, s, why in rows:
    print(f"{n:>3} {d:>6} {r:>4}  {s:<5} {why}")
print("-"*78)
print(f"共 {len(rows)} 頁；通過 {len(rows)-len(fails)}；不通過 {len(fails)} → {fails}")
used = set()
for wk, _ in slides:
    used |= {c.strip() for c in wk.split(",") if c.strip()}
print(f"Wiki 條目使用率：{len(used)}/{len(wiki_codes)} → 未被簡報引用：{sorted(wiki_codes-used)}")
sys.exit(1 if fails else 0)
