# -*- coding: utf-8 -*-
"""G2 忠實度關卡 — SQL 實跑驗證
每個範例宣告 slide 編號、SQL、以及「簡報中宣稱的輸出」。
腳本在 SQLite 實際執行並比對。不符者列為 FAIL，退回 N4 僅重寫該頁。
"""
import sqlite3, sys, json, pathlib

SCHEMA = """
CREATE TABLE department (id INTEGER, name TEXT);
CREATE TABLE employee (id INTEGER, name TEXT, dept_id INTEGER, salary INTEGER);
INSERT INTO department VALUES (1,'工程'), (2,'行銷'), (3,'財務');
INSERT INTO employee VALUES
  (1,'陳怡君',1,62000),
  (2,'林志明',1,58000),
  (3,'王美玲',2,51000),
  (4,'張家豪',NULL,47000);
"""

EXAMPLES = [
 dict(slide=3, label="看一張表的全部內容",
      sql="SELECT * FROM employee;",
      expect=[(1,'陳怡君',1,62000),(2,'林志明',1,58000),(3,'王美玲',2,51000),(4,'張家豪',None,47000)]),

 dict(slide=4, label="SELECT 挑欄位、WHERE 挑列",
      sql="SELECT name, salary FROM employee WHERE dept_id = 1;",
      expect=[('陳怡君',62000),('林志明',58000)]),

 dict(slide=5, label="INNER JOIN：未配對的列被丟棄",
      sql="""SELECT e.name, d.name FROM employee e
             INNER JOIN department d ON e.dept_id = d.id ORDER BY e.id;""",
      expect=[('陳怡君','工程'),('林志明','工程'),('王美玲','行銷')]),

 dict(slide=5, label="LEFT JOIN：左表每列至少出現一次",
      sql="""SELECT e.name, d.name FROM employee e
             LEFT JOIN department d ON e.dept_id = d.id ORDER BY e.id;""",
      expect=[('陳怡君','工程'),('林志明','工程'),('王美玲','行銷'),('張家豪',None)]),

 dict(slide=6, label="條件放 ON：外連接保留未配對列",
      sql="""SELECT e.name, d.name FROM employee e
             LEFT JOIN department d ON e.dept_id = d.id AND d.name = '工程'
             ORDER BY e.id;""",
      expect=[('陳怡君','工程'),('林志明','工程'),('王美玲',None),('張家豪',None)]),

 dict(slide=6, label="條件放 WHERE：外連接退化成內連接",
      sql="""SELECT e.name, d.name FROM employee e
             LEFT JOIN department d ON e.dept_id = d.id
             WHERE d.name = '工程' ORDER BY e.id;""",
      expect=[('陳怡君','工程'),('林志明','工程')]),

 dict(slide=7, label="別名可以用在 ORDER BY",
      sql="SELECT name, salary * 12 AS annual FROM employee ORDER BY annual DESC;",
      expect=[('陳怡君',744000),('林志明',696000),('王美玲',612000),('張家豪',564000)]),

 dict(slide=7, label="別名用在 WHERE：SQLite 接受（非 SQL 標準）",
      sql="SELECT name, salary * 12 AS annual FROM employee WHERE annual > 600000;",
      expect=[('陳怡君',744000),('林志明',696000),('王美玲',612000)]),

 dict(slide=7, label="HAVING 過濾組，WHERE 過濾列",
      sql="""SELECT dept_id, COUNT(*) AS n FROM employee
             GROUP BY dept_id HAVING COUNT(*) >= 2;""",
      expect=[(1,2)]),

 dict(slide=8, label="= NULL 永遠配不到任何列",
      sql="SELECT name FROM employee WHERE dept_id = NULL;",
      expect=[]),

 dict(slide=8, label="IS NULL 才是正確寫法",
      sql="SELECT name FROM employee WHERE dept_id IS NULL;",
      expect=[('張家豪',)]),

 dict(slide=8, label="COUNT(*) 與 COUNT(col) 對 NULL 的差異",
      sql="SELECT COUNT(*), COUNT(dept_id) FROM employee;",
      expect=[(4,3)]),

 dict(slide=11, label="建索引後以索引查找",
      setup="CREATE INDEX idx_emp_dept ON employee(dept_id);",
      sql="EXPLAIN QUERY PLAN SELECT name FROM employee WHERE dept_id = 1;",
      expect_contains="idx_emp_dept"),

 dict(slide=12, label="SQLite：BINARY collation 下 LIKE 前綴【不】走索引",
      setup="CREATE INDEX idx_emp_name ON employee(name);",
      sql="EXPLAIN QUERY PLAN SELECT id FROM employee WHERE name LIKE '陳%';",
      expect_contains="SCAN employee"),

 dict(slide=12, label="SQLite：手寫等價範圍條件則走索引（證明不是索引不能用）",
      sql="EXPLAIN QUERY PLAN SELECT id FROM employee WHERE name >= '陳' AND name < '陳倀';",
      expect_contains="idx_emp_name"),

 dict(slide=12, label="SQLite：欄位改用 NOCASE collation 後 LIKE 前綴走索引",
      setup=("CREATE TABLE emp_nocase (id INTEGER, name TEXT COLLATE NOCASE);"
             "INSERT INTO emp_nocase SELECT id, name FROM employee;"
             "CREATE INDEX idx_nocase_name ON emp_nocase(name);"),
      sql="EXPLAIN QUERY PLAN SELECT id FROM emp_nocase WHERE name LIKE '陳%';",
      expect_contains="idx_nocase_name"),

 dict(slide=12, label="後綴通配 LIKE '%x' 無法用索引",
      sql="EXPLAIN QUERY PLAN SELECT id FROM employee WHERE name LIKE '%君';",
      expect_contains="SCAN employee"),

 dict(slide=12, label="函數包住欄位使索引失效",
      sql="EXPLAIN QUERY PLAN SELECT id FROM employee WHERE UPPER(name) = '陳怡君';",
      expect_contains="SCAN employee"),

 dict(slide=13, label="複合索引：約束前導欄位可用",
      setup="CREATE INDEX idx_emp_dept_salary ON employee(dept_id, salary);",
      sql="EXPLAIN QUERY PLAN SELECT id FROM employee WHERE dept_id = 1 AND salary > 50000;",
      expect_contains="idx_emp_dept_salary"),

 dict(slide=13, label="複合索引：只約束非前導欄位用不到",
      sql="EXPLAIN QUERY PLAN SELECT id FROM employee WHERE salary > 50000;",
      expect_contains="SCAN employee"),

 dict(slide=13, label="覆蓋索引：查詢只要索引內的欄位，不必回表",
      sql="EXPLAIN QUERY PLAN SELECT dept_id, salary FROM employee WHERE dept_id = 1;",
      expect_contains="COVERING INDEX"),

 dict(slide=13, label="非覆蓋：多要一個索引外的欄位就得回表",
      sql="EXPLAIN QUERY PLAN SELECT dept_id, name FROM employee WHERE dept_id = 1;",
      expect_contains="USING INDEX idx_emp_dept"),

 dict(slide=16, label="沒有索引時的計畫：全表掃描",
      sql="EXPLAIN QUERY PLAN SELECT name FROM employee WHERE salary = 62000;",
      expect_contains="SCAN employee"),
]

def run():
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA)
    results = []
    for i, ex in enumerate(EXAMPLES, 1):
        if ex.get("setup"):
            con.executescript(ex["setup"])
        status, got, note = "PASS", None, ""
        try:
            got = con.execute(ex["sql"]).fetchall()
            if ex.get("expect_error"):
                status, note = "FAIL", "預期報錯但成功執行"
            elif "expect_contains" in ex:
                blob = " ".join(str(r) for r in got)
                if ex["expect_contains"] not in blob:
                    status, note = "FAIL", f"輸出未含 {ex['expect_contains']!r}"
            elif got != ex["expect"]:
                status, note = "FAIL", "輸出與宣稱不符"
        except Exception as e:
            if ex.get("expect_error"):
                got, note = f"{type(e).__name__}: {e}", "（符合預期的錯誤）"
            else:
                status, got, note = "FAIL", f"{type(e).__name__}: {e}", "執行失敗"
        results.append(dict(n=i, slide=ex["slide"], label=ex["label"],
                            status=status, got=got, note=note,
                            expect=ex.get("expect", ex.get("expect_contains", "ERROR"))))
    return results

if __name__ == "__main__":
    rs = run()
    nf = 0
    for r in rs:
        mark = "✓" if r["status"] == "PASS" else "✗"
        print(f"{mark} [{r['status']}] #{r['n']:02d} slide {r['slide']:>2} — {r['label']}")
        if r["status"] == "FAIL":
            nf += 1
            print(f"       宣稱：{r['expect']}")
            print(f"       實際：{r['got']}")
            print(f"       原因：{r['note']}")
        elif r["note"]:
            print(f"       {r['note']}  實際：{r['got']}")
    print("-" * 70)
    print(f"共 {len(rs)} 例；通過 {len(rs)-nf}；不通過 {nf}")
    out = pathlib.Path(__file__).resolve().parent / "outputs.json"
    out.write_text(json.dumps(rs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已寫出 {out.name}")
    sys.exit(1 if nf else 0)
