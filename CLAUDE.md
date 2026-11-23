# 交接說明（給 Claude Code）

本資料夾的內容**已經完成**，不需要重新產生任何作業內容。
你唯一的工作是：**把它變成一個 git repo，依階段分次 commit，設好 remote 並 push。**

## 背景

生成式 AI 課程作業。檔案是在 claude.ai 的對話中產生的，透過裝置橋接寫入此資料夾。
該環境的 GitHub push 被政策阻擋、且預設禁止刪除檔案（git 需要刪除 `.lock` 才能運作），
因此 git 操作改由你在本機執行。

## 先做：清除暫存檔

上層資料夾 `..`（即 `生成式AI\`）有兩個傳輸暫存物，請刪除：

- `..\_transfer_sql-wiki.zip`
- `..\_tmp_extract\`（整個資料夾）

## 身分設定

沿用使用者既有的 git 身分（與同層的 `umai_food`、`coc-kp-bot` 一致）：

```
user.name  = HSIN-YU-LIN
user.email = lin0213linasc14@nycu.edu.tw
```

預設分支用 `main`。

## Commit 順序

依 `RUN_LOG.md` 的流程階段分 11 次提交，**依序執行，不要合併**。
每一次都只 `git add` 該階段對應的檔案：

| # | 加入的檔案 | commit message |
|---|---|---|
| 1 | `README.md` `.gitignore` | `init: 專案說明與 loop/graph 設計` |
| 2 | `sources/INDEX.md` | `R2+R4: ingest 來源索引（17 篇一手來源，含兩輪）` |
| 3 | `wiki/` | `R5: 19 條 Wiki 條目（含「寫稿注意」禁區標記）` |
| 4 | `scripts/gate_coverage.py` | `R3: G1 覆蓋率關卡（4 條規則）` |
| 5 | `slides/OUTLINE.md` | `R6: 簡報大綱（18 頁，含每頁 Wiki 條目對應）` |
| 6 | `verify/` | `R7: SQL 實跑驗證（23 個範例，sqlite3）` |
| 7 | `build/index.html` | `R7: 教學簡報 HTML（18 頁）` |
| 8 | `scripts/gate_fidelity.py` | `R8: G2 忠實度關卡（v2：以徽章判定，修正 v1 誤判）` |
| 9 | `scripts/build_wiki_html.py` `build/wiki.html` | `feat: Wiki 網頁版產生器與輸出` |
| 10 | `RUN_LOG.md` | `docs: RUN_LOG 執行紀錄` |
| 11 | `SUBMISSION.md` `CLAUDE.md` | `docs: 繳交說明與反思` |

**不要竄改 commit 時間**（不要用 `--date` 或 `GIT_COMMITTER_DATE` 回溯）。
時間戳集中在同一天是預期的，`README.md` 結尾已就此說明。

## Remote 與 push

```
https://github.com/HSIN-YU-LIN/llm-wiki-sql.git
```

這個 repo **可能尚未在 GitHub 上建立**。先確認：

- 若你有 `gh` 可用：`gh repo create HSIN-YU-LIN/llm-wiki-sql --private --source=. --remote=origin`
  （public 或 private 由使用者決定，預設建議 private，作業繳交後再決定是否公開）
- 若沒有 `gh`：請使用者先到 GitHub 手動建立一個**空的** repo（不要勾選 Add README），
  再 `git remote add origin <url>` 並 `git push -u origin main`

push 前請先向使用者確認 repo 已存在且為空，避免 push 失敗或與既有內容衝突。

## 不要做的事

- 不要重新產生、改寫或「優化」`wiki/`、`build/`、`RUN_LOG.md`、`SUBMISSION.md` 的內容
- 不要修改 commit 時間戳
- 不要把 `README.md` 結尾關於 commit 歷史的說明刪掉（除非使用者明確要求）
