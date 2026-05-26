# 🧪 Vanna-AI 製造業 POC — UI 測試指南

## 📌 測試前準備

1. ✅ 確保伺服器執行中：`python app.py`
2. ✅ 在瀏覽器開啟：`http://localhost:8000`
3. ✅ 看到角色選擇器和查詢介面

---

## 🎯 5 個完整測試用例

### **Test 1️⃣ — 查詢待處理的生產訂單** ✅ 成功

**用途：** 測試作業員可存取的基本查詢

**步驟：**
1. 在「Your Role」選擇 **Operator**
2. 在「Ask a question」輸入：
   ```
   How many production orders are pending?
   ```
3. 點擊 **Submit**

**預期結果：**
- ✅ **狀態：** 成功（綠色訊息）
- **生成的 SQL：**
  ```sql
  SELECT COUNT(*) FROM production_orders WHERE status = 'pending';
  ```
- **結果表：** 顯示 `COUNT(*) = 2`
- **含義：** 有 2 個待處理的生產訂單

**為什麼成功：**
- ✅ 作業員可存取 `production_orders` 表
- ✅ SQL 語法有效

---

### **Test 2️⃣ — 查詢庫存總量** ✅ 成功

**用途：** 測試聚合函數（SUM）

**步驟：**
1. 保持 **Operator** 角色
2. 清空查詢框，輸入：
   ```
   What is the total quantity of inventory items?
   ```
3. 點擊 **Submit**

**預期結果：**
- ✅ **狀態：** 成功（綠色訊息）
- **生成的 SQL：**
  ```sql
  SELECT SUM(quantity_on_hand) AS total_quantity FROM inventory;
  ```
- **結果表：** 顯示 `total_quantity = 3400`
- **含義：** 倉庫中有 3,400 件物品

**為什麼成功：**
- ✅ 作業員可存取 `inventory` 表
- ✅ `SUM()` 函數正確執行

**💡 試試看：** 改問「How many inventory items are below reorder level?」

---

### **Test 3️⃣ — 嘗試查詢產品（被拒絕）** ❌ 權限檢查

**用途：** 測試訪問控制 — 作業員無法查詢 `products` 表

**步驟：**
1. 保持 **Operator** 角色
2. 清空查詢框，輸入：
   ```
   What are all the product names and their prices?
   ```
3. 點擊 **Submit**

**預期結果：**
- ❌ **狀態：** 失敗（紅色錯誤訊息）
- **錯誤訊息：**
  ```
  Access denied. User role 'operator' cannot access table(s): products. 
  Allowed tables: inventory, production_orders
  ```
- **生成的 SQL：**
  ```sql
  SELECT name, unit_price FROM products;
  ```
- **結果表：** 為空（沒有數據）

**為什麼被拒絕：**
- ❌ 作業員的角色無法存取 `products` 表
- ✅ 系統正確攔截未授權查詢

**✨ 現在用主管角色重試：**
1. 改變角色為 **Supervisor**
2. 重新提交相同的問題
3. ✅ 這次應該成功！
   - 會看到 5 個產品的清單

---

### **Test 4️⃣ — 主管無法查詢零件** ❌ 權限檢查

**用途：** 測試分層權限 — 只有總經理可以查詢 `parts`

**步驟：**
1. 改變角色為 **Supervisor**
2. 清空查詢框，輸入：
   ```
   How many parts are used in our products?
   ```
3. 點擊 **Submit**

**預期結果：**
- ❌ **狀態：** 失敗（紅色錯誤訊息）
- **錯誤訊息：**
  ```
  Access denied. User role 'supervisor' cannot access table(s): parts. 
  Allowed tables: inventory, production_orders, products
  ```
- **生成的 SQL：**
  ```sql
  SELECT COUNT(*) as total_parts FROM parts;
  ```
- **結果表：** 為空

**為什麼被拒絕：**
- ❌ 主管無法存取 `parts` 表
- ✅ 系統正確實施分層權限

**✨ 現在用總經理角色重試：**
1. 改變角色為 **Director**
2. 重新提交相同的問題
3. ✅ 這次應該成功！
   - 會看到 `COUNT(*) = 8`（8 個零件）

---

### **Test 5️⃣ — 查詢系統使用者（被拒絕）** ❌ 權限檢查

**用途：** 測試敏感資料保護 — 只有總經理可查詢 `users`

**步驟：**
1. 改變角色為 **Operator**
2. 清空查詢框，輸入：
   ```
   How many users are in the system?
   ```
3. 點擊 **Submit**

**預期結果：**
- ❌ **狀態：** 失敗（紅色錯誤訊息）
- **錯誤訊息：**
  ```
  Access denied. User role 'operator' cannot access table(s): users. 
  Allowed tables: inventory, production_orders
  ```
- **生成的 SQL：**
  ```sql
  SELECT COUNT(*) FROM users;
  ```
- **結果表：** 為空

**為什麼被拒絕：**
- ❌ 作業員無法存取 `users` 表（敏感資料）
- ✅ 系統正確保護敏感資訊

**✨ 現在用總經理角色重試：**
1. 改變角色為 **Director**
2. 重新提交相同的問題
3. ✅ 這次應該成功！
   - 會看到 `COUNT(*) = 5`（5 個使用者）

---

## 📊 角色權限對照表

### 可存取的表格

| 表格 | Operator | Supervisor | Director |
|------|:--------:|:----------:|:--------:|
| `production_orders` | ✅ | ✅ | ✅ |
| `inventory` | ✅ | ✅ | ✅ |
| `products` | ❌ | ✅ | ✅ |
| `parts` | ❌ | ❌ | ✅ |
| `users` | ❌ | ❌ | ✅ |

### 使用者帳戶

可以在 Test 5 中用總經理角色查看完整列表：

```
5 個使用者：
- operator1 (Operator)
- operator2 (Operator)
- supervisor1 (Supervisor)
- supervisor2 (Supervisor)
- director1 (Director)
```

---

## ✅ 測試檢查清單

完成以下所有測試項目：

### 功能性測試
- [ ] Test 1：基本查詢成功（作業員可查詢生產訂單）
- [ ] Test 2：聚合函數正確（SUM 計算正確）
- [ ] Test 3：權限檢查有效（拒絕作業員查詢產品）
- [ ] Test 4：分層權限有效（拒絕主管查詢零件）
- [ ] Test 5：敏感資料保護（拒絕作業員查詢使用者）

### UI 功能
- [ ] 角色選擇器可以切換角色
- [ ] 角色切換時「Available Tables」會更新
- [ ] 成功查詢時顯示綠色成功訊息
- [ ] 失敗查詢時顯示紅色錯誤訊息
- [ ] SQL 查詢正確顯示在「Generated SQL」框中
- [ ] 結果以表格形式正確顯示

### 權限檢查
- [ ] ✅ 作業員：可查詢 2 個表（production_orders, inventory）
- [ ] ✅ 主管：可查詢 3 個表（+ products）
- [ ] ✅ 總經理：可查詢全部 5 個表
- [ ] ✅ 系統拒絕所有未授權查詢

---

## 🎓 進階測試建議

如果基本測試都通過，可以試試以下進階查詢：

### 作業員可以提問的進階查詢
```
1. "Show me all production orders with status in_progress"
2. "Which warehouse has the most inventory?"
3. "What is the average quantity of items in inventory?"
4. "Show all inventory items that are below reorder level"
```

### 主管可以提問的進階查詢
```
1. "What is the most expensive product?"
2. "How many products are in the Electronics category?"
3. "List all products sorted by unit price"
```

### 總經理可以提問的進階查詢
```
1. "How many parts does each product contain?"
2. "List all parts and their associated products"
3. "Show the relationship between products and parts"
```

---

## 🐛 故障排除

| 問題 | 解決方案 |
|------|--------|
| 按 Submit 後沒有反應 | 檢查伺服器是否執行中（`ps aux \| grep app.py`） |
| 看到紅色的「Database error」 | 檢查 `.env` 檔案中的 `OPENROUTER_API_KEY` 是否正確 |
| SQL 包含 markdown 格式（```sql ... ```） | 已修復，請重啟伺服器 |
| 角色切換後表格清單沒更新 | 重新整理瀏覽器（F5） |
| 權限拒絕訊息不清楚 | 這是正常的 — 會告訴你哪個角色、允許哪些表 |

---

## 📝 測試記錄

在下方記錄你的測試結果：

```
日期: _______________
測試者: _______________

Test 1: [ ] 通過  [ ] 失敗
Test 2: [ ] 通過  [ ] 失敗
Test 3: [ ] 通過  [ ] 失敗
Test 4: [ ] 通過  [ ] 失敗
Test 5: [ ] 通過  [ ] 失敗

總體狀態: [ ] 全部通過 ✅  [ ] 有失敗 ❌

備註:
_________________________________________________________________

```

---

## 🎉 完成測試

如果以上所有測試都通過，恭喜！系統已經準備好使用。

**下一步：**
- 試試自己設計的查詢
- 邀請其他人測試
- 收集反饋並改進

祝你測試愉快！🚀
