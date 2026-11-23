# A4 — JOIN 的種類與語意

**來源**：S6
**適用範圍**：PostgreSQL 18 文件；語意為 SQL 標準通用

## 內容（沿用 A1 的 t1 / t2 範例）

- **CROSS JOIN**：笛卡兒積，T1 的每一列與 T2 的每一列配對，N 與 M 列產生 N × M 列。等同於 `INNER JOIN ... ON TRUE`，也等同於用逗號分隔的 FROM 清單。[S6]
- **INNER JOIN**（未加修飾詞時的預設）：對每一對滿足連接條件的 (T1列, T2列) 輸出一列。**兩邊未配對到的列都被丟棄。**[S6]
  - `SELECT * FROM t1 INNER JOIN t2 ON t1.num = t2.num;` → `1 a 1 xxx` / `3 c 3 yyy`
- **LEFT OUTER JOIN**：先做 inner join，再為每一個在 T2 中無配對的 T1 列補上一列，T2 側所有欄位填 NULL。**每一列 T1 至少出現一次。**[S6]
  - 比 inner join 多出：`2 b | NULL | NULL`
- **RIGHT OUTER JOIN**：反向，為每一個未配對的 T2 列補列，T1 側填 NULL。每一列 T2 至少出現一次。[S6]
  - 多出：`NULL | NULL | 5 | zzz`
- **FULL OUTER JOIN**：先做 inner join，再把兩邊未配對的列都補上（各自以 NULL 填滿對側）。[S6]
- `OUTER` 一律可省略；`LEFT`、`RIGHT`、`FULL` 本身就蘊含外連接。[S6]

## ON 與 WHERE 的關鍵差異（外連接才看得出來）

`ON` 接受任何布林運算式，在**連接之前**套用，影響哪些列算配對；`WHERE` 在**連接之後**套用，影響哪些列留下。[S6]

```sql
SELECT * FROM t1 LEFT JOIN t2 ON t1.num = t2.num AND t2.value = 'xxx';
-- 3 列：1 a 1 xxx / 2 b NULL NULL / 3 c NULL NULL

SELECT * FROM t1 LEFT JOIN t2 ON t1.num = t2.num WHERE t2.value = 'xxx';
-- 1 列：1 a 1 xxx
```

內連接時兩種寫法結果相同；**外連接時不同**。[S6]
這是「LEFT JOIN 後面接 WHERE 會把外連接打回內連接」的官方依據。

## ON / USING / NATURAL

- `USING (a, b)` 等價於 `ON T1.a = T2.a AND T1.b = T2.b`，且輸出會把配對欄位合併成一份。用 `ON` 時配對欄位會出現兩次。[S6]
- `NATURAL` 等同於對所有同名欄位做 `USING`。文件明言 NATURAL **比 USING 風險高得多**，因為新增一個同名欄位的綱要變更會無聲地改變連接行為。若兩表無同名欄位，NATURAL 的行為等同 CROSS JOIN。[S6]
