# llm-wiki-sql

生成式 AI 課程作業：建立一個主題式 LLM Wiki，並以該 Wiki 為唯一知識來源，
產出一份教學型 HTML 簡報。

**Wiki 主題**：SQL 查詢的執行與效能
**簡報**：你的查詢為什麼慢？從一次 SELECT 看懂 SQL 怎麼被執行（18 頁，11 頁含實跑 SQL）

## 成果

| 項目 | 位置 |
|---|---|
| Wiki 條目（原始 Markdown） | `wiki/`（19 條，A~D 四類） |
| Wiki 網頁版 | `build/wiki.html` |
| 教學簡報 | `build/index.html` |
| 來源索引 | `sources/INDEX.md`（17 篇一手來源） |
| 簡報大綱與條目對應 | `slides/OUTLINE.md` |
| 執行紀錄 | `RUN_LOG.md` |
| 繳交說明與反思 | `SUBMISSION.md` |

## loop / graph

```
          ┌──────────── 退回：覆蓋不足 → 補 ingest ────────────┐
          ↓                                                   │
    [檢索 Wiki] ─→ [G1 覆蓋率關卡] ─→ [產生大綱] ─→ [人工確認] ┘
                                                     │
                                                     ↓
    [逐頁寫稿] ─→ [G2 忠實度關卡] ─→ [渲染 HTML] ─→ [渲染檢查] ─→ [交件]
          ↑              │                               │
          └── 退回：追不回來 → 只重寫該頁 ──┴───────────────┘
```

兩道關卡都是可執行程式，不是人工目視：

- `scripts/gate_coverage.py` — G1 覆蓋率關卡，4 條規則，受檢對象為 19 條 Wiki 條目
- `scripts/gate_fidelity.py` — G2 忠實度關卡，5 條規則，受檢對象為 18 頁簡報
- `verify/examples.py` — 簡報中 23 段 SQL 以 Python 內建 sqlite3 實際執行並逐字比對輸出

### 重現檢查結果

依序執行（`examples.py` 會產生 `verify/outputs.json`，G2 需要讀它）：

```bash
python3 verify/examples.py        # 23 例 SQL 實跑，並寫出 verify/outputs.json
python3 scripts/gate_coverage.py  # G1 覆蓋率關卡
python3 scripts/gate_fidelity.py  # G2 忠實度關卡
python3 scripts/build_wiki_html.py  # 重新產生 build/wiki.html
```

四支程式的路徑皆由腳本自身位置推導，從任意工作目錄執行皆可，
只需要 Python 3（標準函式庫即可；`build_wiki_html.py` 另需 `markdown` 套件）。

2026-11-23 的執行結果：SQL 23/23 通過、G1 19/19 通過、G2 18/18 通過，
Wiki 條目使用率 19/19（無未被簡報引用的條目）。

## 關於本 repo 的 commit 歷史

本 repo 的 commit 歷史於 2026-11-23 單次建立，依 `RUN_LOG.md` 所載的流程階段分次提交，
並非各階段當時的即時提交紀錄。所有 commit 時間戳均為實際提交時間，未經回溯修改。
