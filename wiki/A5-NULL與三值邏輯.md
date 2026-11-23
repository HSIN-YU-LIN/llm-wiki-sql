# A5 — NULL 與三值邏輯

**來源**：S5, S6
**適用範圍**：PostgreSQL 18 文件；SQL 標準行為

## 內容

- 一般比較運算子（`=`、`<>`、`<` 等）在**任一邊為 null 時回傳 null**（意為 unknown），而非 true 或 false。[S5]
  - `SELECT 7 = NULL;` → null
  - `SELECT 7 <> NULL;` → null
- 原因：NULL 代表未知值，兩個未知值無法被認定相等，所以比較不可能產生 true。[S5]
- 因此 `expression = NULL` **永遠不會配對到任何列**。正確寫法是 `IS NULL` / `IS NOT NULL`。[S5]
- PostgreSQL 提供 `transform_null_equals` 設定，啟用後會把 `x = NULL` 改寫為 `x IS NULL`，但文件建議修正應用程式以符合 SQL 標準，而非依賴此設定。[S5]

## IS DISTINCT FROM

- `IS DISTINCT FROM`：把 null 當成可比較的值。兩邊非 null 時行為同 `<>`；**兩邊都是 null 回傳 false**；**恰好一邊是 null 回傳 true**。[S5]
- `IS NOT DISTINCT FROM`：兩邊非 null 時行為同 `=`；兩邊都 null 回傳 true；恰好一邊 null 回傳 false。[S5]
- 文件說明這組述詞實際上是把 null 當作普通值而非「未知」來處理。[S5]

| 運算式 | 結果 |
|---|---|
| `1 IS DISTINCT FROM NULL` | true |
| `NULL IS DISTINCT FROM NULL` | false |
| `1 IS NOT DISTINCT FROM NULL` | false |
| `NULL IS NOT DISTINCT FROM NULL` | true |

## 布林測試

`IS TRUE` / `IS NOT TRUE` / `IS FALSE` / `IS NOT FALSE` / `IS UNKNOWN` / `IS NOT UNKNOWN` **一律回傳 true 或 false，永不回傳 null**，即使運算元為 null。[S5]

| 運算式 | 結果 |
|---|---|
| `NULL::boolean IS TRUE` | false |
| `NULL::boolean IS NOT TRUE` | true |
| `NULL::boolean IS UNKNOWN` | true |

## 與 A3 的交互作用

`WHERE` 會丟棄條件為 **false 或 NULL** 的列（見 A3 / [S6]）。這代表 NULL 在 WHERE 中的效果等同於 false——這是 NULL 最常造成意外的地方。
