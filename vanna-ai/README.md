# 🏭 Vanna-AI 製造業 POC

用自然語言查詢資料庫的智能系統，整合 OpenRouter AI 和以角色為基礎的存取控制。

## 概述

Vanna-AI 製造業 POC 是一個全端應用程式，讓使用者能用自然語言向資料庫提問，系統自動產生 SQL 查詢語句。本系統使用 OpenRouter 提供的各種 AI 模型，並實作了以角色為基礎的存取控制（RBAC），不同的使用者角色只能存取獲授權的資料表。

**核心特色：**
- 🤖 OpenRouter AI 驅動的自然語言轉 SQL 功能（支援 Claude、Llama、GPT 等模型）
- 🔐 三層角色權限控制（作業員/主管/總經理）
- 📊 製造業資料模型（產品、零件、庫存、生產訂單）
- 🎨 響應式網頁介面
- ✅ 完整的端到端測試

## 快速開始

### 系統需求

- Python 3.9 以上版本
- pip（套件管理器）
- **必須：OPENROUTER_API_KEY**（OpenRouter API 金鑰，可從 [https://openrouter.ai](https://openrouter.ai) 取得）

### 安裝依賴套件

```bash
python -m pip install -r requirements.txt
```

### 設定環境變數

1. **複製範本檔案：**
   ```bash
   cp .env.example .env
   ```

2. **編輯 `.env` 檔案，填入你的 OpenRouter API 金鑰：**
   ```env
   OPENROUTER_API_KEY=sk-or-your-actual-key
   LLM_MODEL=meta-llama/llama-3.1-70b-instruct
   ```

應用程式會自動從 `.env` 檔案讀取這些設定。

### 初始化資料庫

```bash
python data_seed.py
```

輸出：`✓ Database created at manufacturing.db`

### 啟動伺服器

```bash
python app.py
```

伺服器將在 `http://localhost:8000` 執行

用瀏覽器開啟網址，選擇使用者角色，輸入自然語言問題，查看產生的 SQL 和查詢結果。

## 專案結構

```
vanna-ai/
├── app.py                    # FastAPI 伺服器
├── data_seed.py             # 資料庫初始化指令碼
├── requirements.txt         # 專案依賴
├── manufacturing.db         # SQLite 資料庫（自動產生）
├── utils/
│   ├── __init__.py
│   └── access_control.py    # 角色權限控制工具
├── static/
│   └── index.html          # 前端使用者介面
└── README.md               # 本檔案
```

## API 端點

### GET `/`
傳回前端 HTML 介面。

```bash
curl http://localhost:8000/
```

### GET `/tables`
取得目前使用者角色可存取的資料表及欄位資訊。

```bash
curl "http://localhost:8000/tables?user_role=operator"
```

**參數：**
- `user_role`: 使用者角色（`operator`、`supervisor`、`director`）

**回應：**
```json
{
  "tables": {
    "inventory": ["id", "part_id", "warehouse_location", ...],
    "production_orders": ["id", "product_id", "order_date", ...]
  },
  "role": "operator"
}
```

### POST `/ask`
提交自然語言問題，產生 SQL 並執行查詢。

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "有多少個生產訂單？", "user_role": "operator"}'
```

**要求本體：**
```json
{
  "question": "自然語言問題",
  "user_role": "operator"
}
```

**回應：**
```json
{
  "sql": "SELECT COUNT(*) FROM production_orders",
  "results": [{"COUNT(*)": 5}],
  "columns": ["COUNT(*)"],
  "error": null
}
```

## 角色和權限

| 角色 | 可存取的表 | 說明 |
|------|----------|------|
| **作業員** (operator) | production_orders、inventory | 查看生產訂單和庫存 |
| **主管** (supervisor) | production_orders、inventory、products | 可額外查看產品資訊 |
| **總經理** (director) | products、parts、inventory、production_orders、users | 完全存取權限 |

當存取被拒絕時，API 會傳回錯誤訊息：
```json
{
  "sql": "SELECT * FROM users",
  "results": [],
  "columns": [],
  "error": "Access denied. User role 'operator' cannot access table(s): users"
}
```

## 資料庫架構

### 表結構

**products** — 產品資訊
```
id、name、category、unit_price、lead_time_days
```

**parts** — 零件資訊
```
id、name、product_id、quantity_per_unit
外鍵：product_id → products.id
```

**inventory** — 庫存紀錄
```
id、part_id、warehouse_location、quantity_on_hand、reorder_level
外鍵：part_id → parts.id
```

**production_orders** — 生產訂單
```
id、product_id、order_date、due_date、status、quantity
外鍵：product_id → products.id
```

**users** — 示範使用者（僅總經理層級可見）
```
id、username、role
```

### 示範資料

- 5 個產品（Widget A/B、Gadget X/Y、Component Z）
- 8 個零件
- 8 筆庫存紀錄
- 5 個生產訂單
- 5 個示範使用者

## 使用範例

### 範例 1：查詢作業員可存取的資料

```bash
# 取得可用的表
curl "http://localhost:8000/tables?user_role=operator"

# 查詢生產訂單
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "顯示所有待處理的生產訂單", "user_role": "operator"}'
```

### 範例 2：存取控制演示

```bash
# 作業員嘗試查詢使用者表（被拒絕）
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "列出所有使用者", "user_role": "operator"}'

# 傳回：Access denied to users table

# 總經理查詢使用者表（成功）
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "列出所有使用者", "user_role": "director"}'
```

## 環境變數

應用程式會自動從 `.env` 檔案讀取下列環境變數：

### OPENROUTER_API_KEY（**必須**）
OpenRouter API 金鑰，用於自然語言 SQL 產生。可於 [https://openrouter.ai](https://openrouter.ai) 註冊取得。

在 `.env` 檔案中設定：
```env
OPENROUTER_API_KEY=sk-or-your-actual-key
```

### LLM_MODEL（選項）
要使用的 AI 模型。預設值：`meta-llama/llama-3.1-70b-instruct`

可用的模型範例：
- `meta-llama/llama-3.1-70b-instruct` — Llama 3.1 70B（預設，快速免費）
- `claude-3.5-sonnet` — Claude 3.5 Sonnet（準確度高）
- `gpt-4o` — OpenAI GPT-4o
- `mistral/mistral-large` — Mistral Large

在 `.env` 檔案中設定自訂模型：
```env
OPENROUTER_API_KEY=sk-or-your-actual-key
LLM_MODEL=claude-3.5-sonnet
```

> **提示：** `.env` 檔案已加入 `.gitignore`，不會被提交到版本控制。請複製 `.env.example` 建立 `.env` 檔案，並填入你的實際 API 金鑰。

若未設定 OPENROUTER_API_KEY，系統會使用模擬 SQL 產生進行測試。

## 技術堆疊

| 組件 | 技術 | 版本 |
|------|------|------|
| 後端框架 | FastAPI | 0.104.1 |
| 伺服器 | Uvicorn | 0.24.0 |
| 資料驗證 | Pydantic | 2.5.0 |
| AI 整合 | OpenAI SDK（for OpenRouter） | ≥1.0.0 |
| SQL 工具 | Vanna | 0.3.0 |
| 資料庫 | SQLite 3 | 內建 |
| 前端 | HTML5/JavaScript | 原生 |

## 開發

### 重新初始化資料庫

```bash
rm manufacturing.db
python data_seed.py
```

### 執行前端測試

用瀏覽器開啟 `http://localhost:8000`，測試：
1. 角色選擇器切換
2. 自然語言查詢提交
3. 結果表顯示
4. 存取控制（作業員無法查看使用者表）

### 檢查日誌

```bash
tail -f server.log
```

## 資安

- ✅ 基於表的存取控制，在查詢執行前驗證
- ✅ XSS 防護：使用 `textContent` 而非 `innerHTML`
- ✅ SQL 驗證：檢查查詢中的表名是否在允許清單中
- ✅ 回應驗證：確保伺服器傳回的資料結構有效
- ✅ 無 SQL 注入風險：由 Claude 產生的 SQL 經過驗證後執行

## 常見問題

**Q：沒有 ANTHROPIC_API_KEY 時會發生什麼？**  
A：系統使用模擬 SQL 產生傳回範例查詢，適合演示和測試。

**Q：要如何修改角色權限？**  
A：編輯 `utils/access_control.py` 中的 `ROLE_PERMISSIONS` 字典。

**Q：要如何新增新的表到資料庫？**  
A：在 `data_seed.py` 的 `create_schema()` 函式中新增 CREATE TABLE 語句，並在 `utils/access_control.py` 的 `ROLE_PERMISSIONS` 中設定權限。

**Q：支援哪些資料庫？**  
A：目前實作使用 SQLite。若要支援其他資料庫（PostgreSQL、MySQL），需修改資料庫連線邏輯。

## 授權

MIT

## 聯絡方式

如有問題或建議，請提交 Issue 或聯絡開發團隊。

---

**最後更新：** 2026-05-26  
**版本：** 1.0.0（POC）
