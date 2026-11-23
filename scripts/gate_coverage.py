import os, re, sys, json, pathlib

WIKI = str(pathlib.Path(__file__).resolve().parent.parent / "wiki")
rows, fails = [], []

for fn in sorted(os.listdir(WIKI)):
    if not fn.endswith(".md"):
        continue
    text = open(os.path.join(WIKI, fn), encoding="utf-8").read()
    code = fn.split("-")[0]

    m = re.search(r"\*\*來源\*\*：(.+)", text)
    declared = sorted(set(re.findall(r"S\d+", m.group(1)))) if m else []

    cited = sorted(set(re.findall(r"\[(S\d+)(?:\]\[S\d+)*\]", text)))
    cited = sorted(set(re.findall(r"S\d+", " ".join(re.findall(r"\[([^\]]*S\d+[^\]]*)\]", text)))))
    n_cites = len(re.findall(r"\[S\d+\]", text))
    has_gap = "覆蓋缺口" in text
    body = re.sub(r"⚠ 覆蓋缺口[\s\S]*", "", text)
    n_cites_body = len(re.findall(r"\[S\d+\]", body))

    reasons = []
    if not declared:
        reasons.append("未宣告來源")
    if n_cites_body < 3:
        reasons.append(f"本文引註過少({n_cites_body}<3)")
    if has_gap:
        reasons.append("自述覆蓋缺口")
    undeclared = [c for c in cited if c not in declared]
    if undeclared:
        reasons.append("引用未宣告來源:" + ",".join(undeclared))

    status = "PASS" if not reasons else "FAIL"
    rows.append((code, fn, len(declared), n_cites_body, status, "; ".join(reasons)))
    if reasons:
        fails.append(code)

w = max(len(r[1]) for r in rows)
print(f"{'條目':<5} {'檔名':<{w}} {'來源數':>6} {'引註數':>6}  {'判定':<5} 原因")
print("-" * (w + 50))
for c, fn, d, n, s, r in rows:
    print(f"{c:<5} {fn:<{w}} {d:>6} {n:>6}  {s:<5} {r}")
print("-" * (w + 50))
print(f"總條目 {len(rows)}；通過 {len(rows)-len(fails)}；不通過 {len(fails)} → {fails}")
sys.exit(1 if fails else 0)
