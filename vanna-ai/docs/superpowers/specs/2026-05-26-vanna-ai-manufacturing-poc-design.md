# Vanna-AI Manufacturing POC Design

**Date:** 2026-05-26  
**Status:** Approved  
**Scope:** Proof of concept for text-to-SQL system using Vanna-AI with manufacturing data

---

## 1. Overview

Build a working POC that demonstrates Vanna-AI's text-to-SQL capabilities using a manufacturing industry dataset. The system accepts natural language queries and generates correct SQL against a manufacturing schema.

### Success Criteria
- ✅ FastAPI server runs locally
- ✅ Web UI accessible at `http://localhost:8000`
- ✅ Accept natural language queries and return SQL + results
- ✅ Realistic manufacturing schema with proper relationships
- ✅ LLM (Claude) successfully generates correct SQL

---

## 2. Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────────────┐
│            Browser Frontend (HTML/JS)               │
│  - Query input box                                  │
│  - Results table display                            │
│  - Schema browser                                   │
│  - Generated SQL viewer                             │
└──────────────┬──────────────────────────────────────┘
               │ HTTP
               ↓
┌─────────────────────────────────────────────────────┐
│         FastAPI Server (app.py)                     │
│  - POST /ask - Natural language to SQL              │
│  - GET /tables - Schema information                 │
│  - Vanna Agent instance                             │
│  - Claude LLM service                               │
│  - Agent memory (DemoAgentMemory)                   │
└──────────────┬──────────────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────────┐
│     SQLite Database (manufacturing.db)              │
│  - products                                         │
│  - parts                                            │
│  - inventory                                        │
│  - production_orders                                │
└─────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Vanna-AI (text-to-SQL orchestration)
- Claude Sonnet 4.5 (LLM, via Anthropic API)
- SQLite (embedded database)
- Python 3.9+

**Frontend:**
- HTML5 + vanilla JavaScript
- CSS (inline)
- No build tools required

### 2.3 Access Control Architecture

Three role-based access groups with table-level permissions:

```
User → Role (Operator/Supervisor/Director) → Accessible Tables
  
Operator:
  - production_orders (read only)
  - inventory (read only)

Supervisor:
  - production_orders (read only)
  - inventory (read only)
  - products (read only)

Director:
  - All tables (full read access)
```

Each query is validated against user's role before execution.

---

## 3. Database Schema

### 3.1 Manufacturing Tables

**products**
```sql
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  unit_price REAL,
  lead_time_days INTEGER
);
```

**parts**
```sql
CREATE TABLE parts (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  product_id INTEGER NOT NULL,
  quantity_per_unit INTEGER,
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**inventory**
```sql
CREATE TABLE inventory (
  id INTEGER PRIMARY KEY,
  part_id INTEGER NOT NULL,
  warehouse_location TEXT,
  quantity_on_hand INTEGER,
  reorder_level INTEGER,
  FOREIGN KEY (part_id) REFERENCES parts(id)
);
```

**production_orders**
```sql
CREATE TABLE production_orders (
  id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL,
  order_date TEXT,
  due_date TEXT,
  status TEXT,  -- 'pending', 'in_progress', 'completed'
  quantity INTEGER,
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**users** (for demo/testing)
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL  -- 'operator', 'supervisor', 'director'
);
```

### 3.2 Sample Data
- 20-30 products (various manufacturing categories)
- 60-100 parts (components across products)
- 100+ inventory records (realistic stock levels)
- 50-100 production orders (mix of statuses)
- 5 demo users:
  - operator1 (role: operator)
  - supervisor1 (role: supervisor)
  - director1 (role: director)
  - operator2, supervisor2 (additional test accounts)

---

## 4. Backend Implementation

### 4.1 File: `app.py`

Main FastAPI server with:

1. **Initialization**
   - Load SQLite database (manufacturing.db)
   - Initialize Anthropic Claude LLM service
   - Create Vanna Agent with DemoAgentMemory
   - Register SQL execution tool with access control

2. **Endpoints**
   - `GET /` - Serve static/index.html
   - `GET /tables` - Return list of tables and columns (filtered by user role)
   - `POST /ask` - Accept query + user role, return SQL + results
     - Input: `{ "question": "...", "user_role": "operator|supervisor|director" }`
     - Output: `{ "sql": "...", "results": [...], "columns": [...], "error": null }`
   - Validates generated SQL against user's allowed tables before execution

3. **Access Control**
   - Role-based filtering: before returning results, check if user can access the queried tables
   - Operator: production_orders, inventory
   - Supervisor: production_orders, inventory, products
   - Director: all tables
   - Return clear error if user tries to query inaccessible table

4. **Error Handling**
   - Invalid SQL catches and returns friendly messages
   - Access denied errors (user queried unauthorized table)
   - Missing API key validation
   - Database connection errors

### 4.2 Agent Memory

Pre-load DemoAgentMemory with 5-10 example question-SQL pairs:
- "Show slow-moving inventory" → SELECT inventory with quantity > reorder_level
- "Which products are overdue?" → SELECT production_orders with due_date < today and status != 'completed'
- "Part availability by warehouse" → SELECT parts with inventory by location
- etc.

This gives Claude context for generating better SQL.

### 4.3 Access Control Helper

Create `utils/access_control.py` with:
- `ROLE_PERMISSIONS` dict mapping roles to allowed tables
- `validate_query_access(sql: str, user_role: str) -> bool` function
- `filter_schema_by_role(tables: list, user_role: str) -> list` function

These utility functions are used by app.py endpoints to enforce permissions.

---

## 5. Frontend Implementation

### 5.1 File: `static/index.html`

Single-page interface with sections:

1. **Header** - Title, brief description
2. **User Role Selector** - Dropdown to select role (operator/supervisor/director)
   - Default: operator
   - Updates available tables dynamically
3. **Query Input** - Text input + Submit button
4. **Schema Panel** - Collapsible section showing available tables/columns (filtered by role)
5. **Results Panel**
   - Display generated SQL (read-only)
   - Display results in table format
   - Show row count and execution status
6. **Error Display** - Clear error messages (including access denied)

### 5.2 JavaScript Behavior

- User selects role from dropdown
- Fetch `/tables` with selected role to populate schema panel
- Submit query via fetch to `/ask` with question + user_role
- Parse JSON response
- Render results table dynamically
- Display SQL for transparency
- Handle loading states and errors
- Handle access denied errors gracefully

---

## 6. Data Seeding

### 6.1 File: `data_seed.py`

Script to:
1. Create SQLite database and schema
2. Insert sample manufacturing data
3. Initialize Vanna agent memory with example queries

Run once: `python data_seed.py`

---

## 7. Development & Deployment

### 7.1 Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Seed database
python data_seed.py

# Run server
python app.py
```

Server runs on `http://localhost:8000`

### 7.2 Environment Variables

Required:
- `ANTHROPIC_API_KEY` - Claude API key

Optional:
- `DATABASE_PATH` - SQLite file path (default: `./manufacturing.db`)
- `PORT` - Server port (default: 8000)

---

## 8. Testing & Validation

### 8.1 Manual Testing

Test queries:
1. "List all products" - Simple SELECT
2. "Which parts go into product 1?" - JOIN (products ← parts)
3. "Show inventory below reorder level" - WHERE clause
4. "Products with most complex assembly" - COUNT/GROUP BY
5. "Production orders due this week" - Date filtering

### 8.2 Success Indicators

- All queries return correct SQL
- Results match expected data
- UI loads without errors
- No SQL injection vulnerabilities

---

## 9. Project Structure

```
vanna-ai/
├── app.py                    # FastAPI server (main)
├── data_seed.py             # Database initialization
├── requirements.txt         # Python dependencies
├── manufacturing.db         # SQLite database (generated)
├── utils/
│   └── access_control.py    # Role-based access control utilities
├── static/
│   └── index.html          # Frontend (single HTML file)
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-05-26-vanna-ai-manufacturing-poc-design.md
└── README.md               # Quick start guide
```

---

## 10. Known Limitations & Future Work

**POC Scope (In Scope):**
- Role-based access control (3 roles: operator, supervisor, director)
- Table-level permission enforcement
- Demo user accounts for testing

**POC Scope (Out of Scope):**
- User authentication (passwords, login system) - demo only uses role selection
- Multi-user session management
- Caching optimization
- Advanced analytics
- Custom SQL validation
- Row-level security
- Audit logging

**Future Enhancements:**
- Add proper user authentication (login/password)
- Persist learned queries
- Add more industry schemas
- Fine-tune Claude with domain-specific prompts
- Export results to CSV/Excel
- Query history/favorites
- Row-level security (filter by department, etc.)
- Audit trails for compliance

---

## 11. Dependencies

- `vanna[anthropic,fastapi]` - Core Vanna-AI
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `anthropic` - Claude API client
- `pydantic` - Data validation

See `requirements.txt` for pinned versions.
