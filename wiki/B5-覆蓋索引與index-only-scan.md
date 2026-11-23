# B5 — 覆蓋索引與 index-only scan

**來源**：S4, S8, S10
**適用範圍**：PostgreSQL 18 機制說明；MySQL 8.0 對應概念

## 定義

**index-only scan** 只用索引項目回答查詢，不回表（heap）取對應的資料列。一般索引掃描必須同時讀索引與 heap，而 heap 的讀取往往是分散的，所以省掉它能大幅節省 I/O。[S4]

## 必要條件

1. **索引型別須支援**。B-tree 永遠支援；GiST 與 SP-GiST 僅部分 operator class 支援；其他型別（含 GIN）不支援。索引必須儲存或能重建每筆項目的原始值——GIN 項目通常只存部分值，故不合格。[S4]
2. **查詢只能參照索引中儲存的欄位**。以表上有 x, y, z、索引建在 `(x, y)` 為例：[S4]
   ```sql
   SELECT x, y FROM tab WHERE x = 'key';         -- 可用
   SELECT x    FROM tab WHERE x = 'key' AND y < 42;  -- 可用
   SELECT x, z FROM tab WHERE x = 'key';         -- 不可用
   SELECT x    FROM tab WHERE x = 'key' AND z < 42;  -- 不可用
   ```

## 為什麼還是常常要回表（PostgreSQL 特有）

- MVCC 下的**列可見性只記錄在 heap tuple 中，不在索引項目裡**。[S4]
- 每個表頁在**可見性映射（visibility map）**中有一個位元，當該頁上所有列對所有現在與未來的交易都可見時被設定。掃描時對每筆候選索引項目檢查對應 heap 頁的該位元：[S4]
  - **位元已設**：該列確定可見，直接回傳索引中的值
  - **位元未設**：必須讀 heap tuple 檢查可見性，相對一般索引掃描**沒有節省**
- 可見性映射比它所描述的 heap 小約四個數量級，通常快取在記憶體中。因此 index-only scan 只有在表中相當大比例的頁都是 all-visible 時才划算——這對**大致靜態的資料**很常見。[S4]

## INCLUDE 覆蓋索引

```sql
CREATE INDEX tab_x_y ON tab (x) INCLUDE (y);
```
- `y` 存在索引中但**不屬於搜尋鍵**，不被索引機制解讀，因此不需要是索引能處理的型別。[S4]
- 唯一性只約束鍵欄位：`CREATE UNIQUE INDEX tab_x_y ON tab (x) INCLUDE (y);` 僅對 `x` 唯一。[S4]
- **代價**：payload 欄位重複表中資料、使索引變大，可能拖慢搜尋；過寬的欄位可能使 tuple 超過索引最大尺寸導致 insert 失敗。只有在表變動夠慢、index-only scan 真能避開回表時才有幫助。[S4]
- 限制：運算式不能作為 included 欄位；只有 B-tree、GiST、SP-GiST 支援 `INCLUDE`。[S4]
- `INCLUDE` 出現之前的做法是把 `y` 當成尾端鍵欄位 `CREATE INDEX tab_x_y ON tab (x, y);`。查找可行，但無法只對 `x` 強制唯一。非鍵欄位也不會進入 B-tree 上層，使上層 tuple 保持精簡。[S4]

## MySQL 的對應說法

查詢只需要索引中包含的欄位時，值直接從索引樹讀出，不查資料列——這就是覆蓋索引。[S8]
在 `EXPLAIN` 的 `Extra` 欄位顯示為 **Using index**。[S10]
