# Vanna-AI Manufacturing POC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working text-to-SQL POC with manufacturing data, Claude LLM integration, and role-based access control (Operator/Supervisor/Director).

**Architecture:** FastAPI backend running Vanna-AI agent with SQLite database + custom HTML/JS frontend with role selector. Access control enforces table-level permissions based on user role.

**Tech Stack:** Python 3.9+, FastAPI, Vanna-AI, Claude Sonnet 4.5, SQLite, vanilla HTML/JS

---

## File Structure

```
vanna-ai/
├── app.py                    # FastAPI server
├── data_seed.py             # Database initialization
├── requirements.txt         # Dependencies
├── manufacturing.db         # SQLite (generated)
├── utils/
│   └── access_control.py    # Role-based access utilities
├── static/
│   └── index.html          # Frontend UI
└── docs/superpowers/specs/  # Design doc (already exists)
```

---

## Phase 1: Project Setup & Dependencies

### Task 1: Create requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Create requirements.txt with all dependencies**

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
anthropic==0.7.1
vanna==0.3.0
```

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "chore: add project dependencies"
```

---

## Phase 2: Database & Access Control

### Task 2: Create access control utilities

**Files:**
- Create: `utils/__init__.py` (empty)
- Create: `utils/access_control.py`

- [ ] **Step 1: Create utils directory structure**

```bash
mkdir -p utils
touch utils/__init__.py
```

- [ ] **Step 2: Write access_control.py with role definitions and validation**

```python
# utils/access_control.py

ROLE_PERMISSIONS = {
    "operator": ["production_orders", "inventory"],
    "supervisor": ["production_orders", "inventory", "products"],
    "director": ["products", "parts", "inventory", "production_orders", "users"],
}

VALID_ROLES = list(ROLE_PERMISSIONS.keys())


def validate_query_access(sql: str, user_role: str) -> tuple[bool, str]:
    """
    Validate if user can execute a query based on their role.
    
    Returns: (is_allowed: bool, error_message: str)
    """
    if user_role not in VALID_ROLES:
        return False, f"Invalid role: {user_role}"
    
    sql_upper = sql.upper()
    allowed_tables = ROLE_PERMISSIONS[user_role]
    
    # Simple check: if the SQL contains a table name not in allowed list, deny
    for table in ROLE_PERMISSIONS["director"]:  # all tables
        if table.upper() in sql_upper:
            if table not in allowed_tables:
                return False, f"Access denied: {table} is not accessible to {user_role}"
    
    return True, ""


def filter_schema_by_role(tables_with_columns: dict, user_role: str) -> dict:
    """
    Filter schema to only include tables accessible by user's role.
    
    Input: {"table_name": ["col1", "col2"], ...}
    Output: filtered version based on role permissions
    """
    if user_role not in VALID_ROLES:
        return {}
    
    allowed_tables = ROLE_PERMISSIONS[user_role]
    return {k: v for k, v in tables_with_columns.items() if k in allowed_tables}
```

- [ ] **Step 3: Commit**

```bash
git add utils/
git commit -m "feat: add role-based access control utilities"
```

---

### Task 3: Create data_seed.py

**Files:**
- Create: `data_seed.py`

- [ ] **Step 1: Write data_seed.py with database schema and sample data**

```python
# data_seed.py

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "manufacturing.db"


def create_schema(conn):
    """Create manufacturing schema."""
    cursor = conn.cursor()
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            unit_price REAL,
            lead_time_days INTEGER
        )
    """)
    
    # Parts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity_per_unit INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            part_id INTEGER NOT NULL,
            warehouse_location TEXT,
            quantity_on_hand INTEGER,
            reorder_level INTEGER,
            FOREIGN KEY (part_id) REFERENCES parts(id)
        )
    """)
    
    # Production orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS production_orders (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            order_date TEXT,
            due_date TEXT,
            status TEXT,
            quantity INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Users table (for demo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL
        )
    """)
    
    conn.commit()


def seed_data(conn):
    """Seed database with sample manufacturing data."""
    cursor = conn.cursor()
    
    # Products
    products = [
        ("Widget A", "Assembly", 199.99, 5),
        ("Widget B", "Assembly", 249.99, 7),
        ("Gadget X", "Electronics", 99.99, 10),
        ("Gadget Y", "Electronics", 149.99, 14),
        ("Component Z", "Parts", 49.99, 3),
    ]
    cursor.executemany(
        "INSERT INTO products (name, category, unit_price, lead_time_days) VALUES (?, ?, ?, ?)",
        products
    )
    
    # Parts
    parts = [
        ("Spring", 1, 2),
        ("Bolt", 1, 4),
        ("Washer", 1, 8),
        ("Resistor", 3, 10),
        ("Capacitor", 3, 5),
        ("Diode", 4, 8),
        ("Connector", 4, 3),
        ("Screw", 2, 6),
    ]
    cursor.executemany(
        "INSERT INTO parts (name, product_id, quantity_per_unit) VALUES (?, ?, ?)",
        parts
    )
    
    # Inventory (randomized levels)
    inventory = [
        (1, "Warehouse A", 150, 50),
        (2, "Warehouse B", 80, 40),
        (3, "Warehouse A", 200, 100),
        (4, "Warehouse C", 30, 50),
        (5, "Warehouse B", 120, 80),
        (6, "Warehouse A", 90, 60),
        (7, "Warehouse C", 45, 30),
        (8, "Warehouse B", 300, 200),
    ]
    cursor.executemany(
        "INSERT INTO inventory (part_id, warehouse_location, quantity_on_hand, reorder_level) VALUES (?, ?, ?, ?)",
        inventory
    )
    
    # Production orders
    today = datetime.now()
    orders = [
        (1, today.strftime("%Y-%m-%d"), (today + timedelta(days=5)).strftime("%Y-%m-%d"), "pending", 100),
        (2, (today - timedelta(days=2)).strftime("%Y-%m-%d"), (today + timedelta(days=3)).strftime("%Y-%m-%d"), "in_progress", 50),
        (3, (today - timedelta(days=10)).strftime("%Y-%m-%d"), (today - timedelta(days=2)).strftime("%Y-%m-%d"), "completed", 75),
        (4, today.strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d"), "pending", 25),
        (1, (today - timedelta(days=5)).strftime("%Y-%m-%d"), (today + timedelta(days=1)).strftime("%Y-%m-%d"), "in_progress", 60),
    ]
    cursor.executemany(
        "INSERT INTO production_orders (product_id, order_date, due_date, status, quantity) VALUES (?, ?, ?, ?, ?)",
        orders
    )
    
    # Demo users
    users = [
        ("operator1", "operator"),
        ("operator2", "operator"),
        ("supervisor1", "supervisor"),
        ("supervisor2", "supervisor"),
        ("director1", "director"),
    ]
    cursor.executemany(
        "INSERT INTO users (username, role) VALUES (?, ?)",
        users
    )
    
    conn.commit()


def main():
    """Initialize database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        create_schema(conn)
        seed_data(conn)
        conn.close()
        print(f"✓ Database created at {DB_PATH}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test data_seed.py**

```bash
python data_seed.py
```

Expected output:
```
✓ Database created at manufacturing.db
```

- [ ] **Step 3: Verify database was created**

```bash
ls -lh manufacturing.db
sqlite3 manufacturing.db "SELECT count(*) FROM products;"
```

Expected: manufacturing.db exists, products table has 5 rows

- [ ] **Step 4: Commit**

```bash
git add data_seed.py
git commit -m "feat: add database initialization script with manufacturing data"
```

---

## Phase 3: Backend Server

### Task 4: Create FastAPI server (app.py)

**Files:**
- Create: `app.py`

- [ ] **Step 1: Write app.py - initialization and helper functions**

```python
# app.py

import sqlite3
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from anthropic import Anthropic
from utils.access_control import validate_query_access, filter_schema_by_role

DB_PATH = "manufacturing.db"
STATIC_DIR = "static"

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize Anthropic client
client = Anthropic()

# System prompt for Claude
SYSTEM_PROMPT = """You are a SQL expert for a manufacturing database. 
Generate SQL queries based on natural language questions.
The database has these tables: products, parts, inventory, production_orders, users.

Key relationships:
- products.id → parts.product_id
- parts.id → inventory.part_id
- products.id → production_orders.product_id

When generating SQL:
1. Use exact table and column names
2. Return valid SQLite syntax
3. Only SELECT queries are allowed
4. Always include relevant table joins for complete results

Respond ONLY with the SQL query, no explanation."""


def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_schema() -> dict:
    """Get database schema (all tables and columns)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    schema = {}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        schema[table_name] = columns
    
    conn.close()
    return schema


def generate_sql(question: str) -> str:
    """Use Claude to generate SQL from natural language."""
    schema = get_schema()
    schema_text = json.dumps(schema, indent=2)
    
    prompt = f"""Given this database schema:
{schema_text}

Generate a SQL query for this question: {question}

Return only the SQL query."""
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    sql = message.content[0].text.strip()
    return sql


def execute_sql(sql: str) -> tuple[list, list]:
    """Execute SQL and return results + column names."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Get results
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results, columns
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")


@app.get("/")
async def read_root():
    """Serve index.html."""
    return FileResponse(f"{STATIC_DIR}/index.html")


@app.get("/tables")
async def get_tables(user_role: str = "operator"):
    """Get available tables for a user role."""
    full_schema = get_schema()
    filtered_schema = filter_schema_by_role(full_schema, user_role)
    
    if not filtered_schema:
        raise HTTPException(status_code=400, detail=f"Invalid role: {user_role}")
    
    return {"tables": filtered_schema, "role": user_role}


class QueryRequest(BaseModel):
    question: str
    user_role: str = "operator"


@app.post("/ask")
async def ask_question(request: QueryRequest):
    """Accept natural language query, return SQL and results."""
    user_role = request.user_role
    question = request.question
    
    try:
        # Generate SQL using Claude
        sql = generate_sql(question)
        
        # Validate access
        is_allowed, error_msg = validate_query_access(sql, user_role)
        if not is_allowed:
            return {
                "sql": sql,
                "results": [],
                "columns": [],
                "error": error_msg
            }
        
        # Execute query
        results, columns = execute_sql(sql)
        
        return {
            "sql": sql,
            "results": results,
            "columns": columns,
            "error": None
        }
    except Exception as e:
        return {
            "sql": "",
            "results": [],
            "columns": [],
            "error": f"Error: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 2: Test that imports work and server starts**

```bash
python -m pip install -q -r requirements.txt
python app.py &
sleep 2
curl http://localhost:8000/
pkill -f "python app.py"
```

Expected: Server starts, returns HTML content, shuts down cleanly

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: create FastAPI server with text-to-SQL agent"
```

---

## Phase 4: Frontend

### Task 5: Create static/index.html

**Files:**
- Create: `static/index.html`

- [ ] **Step 1: Create static directory**

```bash
mkdir -p static
```

- [ ] **Step 2: Write index.html with safe DOM manipulation**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanna-AI Manufacturing POC</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 30px;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
        
        .section {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
        }
        
        .section h2 {
            font-size: 16px;
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .role-selector {
            margin-bottom: 20px;
        }
        
        .role-selector label {
            display: block;
            font-weight: 500;
            margin-bottom: 8px;
            color: #333;
        }
        
        .role-selector select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            background-color: #f9f9f9;
            cursor: pointer;
        }
        
        .role-selector select:hover {
            border-color: #667eea;
        }
        
        .query-input {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .query-input input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .query-input button {
            padding: 12px 25px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.3s;
        }
        
        .query-input button:hover {
            background: #764ba2;
        }
        
        .query-input button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
            font-weight: 500;
        }
        
        .loading.active {
            display: block;
        }
        
        .schema-panel {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .table-group {
            margin-bottom: 15px;
        }
        
        .table-group h3 {
            font-size: 13px;
            color: #333;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .columns {
            padding-left: 15px;
            font-size: 12px;
            color: #666;
            line-height: 1.6;
        }
        
        .column-item {
            padding: 4px 0;
            color: #764ba2;
            font-family: monospace;
        }
        
        .results-section {
            grid-column: 1 / -1;
        }
        
        .error {
            background: #fee;
            border-left: 4px solid #f44;
            padding: 12px;
            border-radius: 4px;
            color: #c33;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .success {
            background: #efe;
            border-left: 4px solid #4f4;
            padding: 12px;
            border-radius: 4px;
            color: #3a3;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .sql-box {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
            border: 1px solid #ddd;
        }
        
        .results-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        
        .results-table th {
            background: #667eea;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }
        
        .results-table td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        
        .results-table tr:hover {
            background: #f9f9f9;
        }
        
        .row-count {
            color: #666;
            font-size: 12px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Vanna-AI Manufacturing POC</h1>
            <p>Natural Language to SQL powered by Claude</p>
        </div>
        
        <div class="content">
            <!-- Left Panel: Query & Schema -->
            <div>
                <div class="section">
                    <h2>Query Interface</h2>
                    
                    <div class="role-selector">
                        <label for="role-select">Your Role:</label>
                        <select id="role-select">
                            <option value="operator">Operator (Limited Access)</option>
                            <option value="supervisor">Supervisor</option>
                            <option value="director">Director (Full Access)</option>
                        </select>
                    </div>
                    
                    <div class="query-input">
                        <input 
                            type="text" 
                            id="question" 
                            placeholder="Ask a question about manufacturing data..."
                        >
                        <button id="submit-btn">Submit</button>
                    </div>
                    
                    <div class="loading" id="loading">⏳ Generating SQL...</div>
                </div>
                
                <div class="section">
                    <h2>Available Tables</h2>
                    <div class="schema-panel" id="schema-panel">
                        <p style="color: #999; font-size: 12px;">Select a role above to see available tables</p>
                    </div>
                </div>
            </div>
            
            <!-- Right Panel: Results -->
            <div>
                <div class="section results-section">
                    <h2>Results</h2>
                    
                    <div id="error-box"></div>
                    <div id="success-box"></div>
                    
                    <div id="results-container" style="display: none;">
                        <div><strong>Generated SQL:</strong></div>
                        <div class="sql-box" id="sql-display"></div>
                        
                        <div style="margin-top: 20px;">
                            <div><strong>Results:</strong></div>
                            <div style="overflow-x: auto; margin-top: 10px;">
                                <table class="results-table" id="results-table">
                                    <thead id="table-head"></thead>
                                    <tbody id="table-body"></tbody>
                                </table>
                            </div>
                            <div class="row-count" id="row-count"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        document.getElementById('role-select').addEventListener('change', onRoleChange);
        document.getElementById('submit-btn').addEventListener('click', submitQuery);
        document.getElementById('question').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') submitQuery();
        });
        
        async function onRoleChange() {
            const role = document.getElementById('role-select').value;
            await loadSchema(role);
            clearResults();
        }
        
        async function loadSchema(role) {
            try {
                const response = await fetch(`${API_BASE}/tables?user_role=${role}`);
                const data = await response.json();
                
                const schemaPanel = document.getElementById('schema-panel');
                schemaPanel.textContent = '';
                
                for (const [table, columns] of Object.entries(data.tables)) {
                    const tableGroup = document.createElement('div');
                    tableGroup.className = 'table-group';
                    
                    const heading = document.createElement('h3');
                    heading.textContent = '📋 ' + table;
                    tableGroup.appendChild(heading);
                    
                    const columnsList = document.createElement('div');
                    columnsList.className = 'columns';
                    columns.forEach(col => {
                        const colDiv = document.createElement('div');
                        colDiv.className = 'column-item';
                        colDiv.textContent = '• ' + col;
                        columnsList.appendChild(colDiv);
                    });
                    tableGroup.appendChild(columnsList);
                    
                    schemaPanel.appendChild(tableGroup);
                }
            } catch (error) {
                showError(`Failed to load schema: ${error.message}`);
            }
        }
        
        async function submitQuery() {
            const question = document.getElementById('question').value.trim();
            const role = document.getElementById('role-select').value;
            
            if (!question) {
                showError('Please enter a question');
                return;
            }
            
            clearResults();
            showLoading(true);
            
            try {
                const response = await fetch(`${API_BASE}/ask`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question, user_role: role})
                });
                
                const data = await response.json();
                showLoading(false);
                
                if (data.error) {
                    showError(data.error);
                    if (data.sql) {
                        showSQL(data.sql);
                    }
                } else {
                    showSuccess(`Query executed successfully (${data.results.length} rows)`);
                    showSQL(data.sql);
                    displayResults(data.results, data.columns);
                }
            } catch (error) {
                showLoading(false);
                showError(`Request failed: ${error.message}`);
            }
        }
        
        function showLoading(isLoading) {
            document.getElementById('loading').classList.toggle('active', isLoading);
            document.getElementById('submit-btn').disabled = isLoading;
        }
        
        function showError(msg) {
            const box = document.getElementById('error-box');
            box.textContent = '';
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = msg;
            box.appendChild(errorDiv);
            document.getElementById('success-box').textContent = '';
        }
        
        function showSuccess(msg) {
            const box = document.getElementById('success-box');
            box.textContent = '';
            const successDiv = document.createElement('div');
            successDiv.className = 'success';
            successDiv.textContent = '✓ ' + msg;
            box.appendChild(successDiv);
            document.getElementById('error-box').textContent = '';
        }
        
        function showSQL(sql) {
            document.getElementById('sql-display').textContent = sql;
        }
        
        function displayResults(results, columns) {
            const container = document.getElementById('results-container');
            const thead = document.getElementById('table-head');
            const tbody = document.getElementById('table-body');
            
            thead.textContent = '';
            tbody.textContent = '';
            
            const headerRow = document.createElement('tr');
            columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            
            results.forEach(row => {
                const tr = document.createElement('tr');
                columns.forEach(col => {
                    const td = document.createElement('td');
                    td.textContent = row[col] ?? '';
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            
            document.getElementById('row-count').textContent = `${results.length} row(s) returned`;
            container.style.display = 'block';
        }
        
        function clearResults() {
            document.getElementById('results-container').style.display = 'none';
            document.getElementById('error-box').textContent = '';
            document.getElementById('success-box').textContent = '';
        }
        
        window.addEventListener('DOMContentLoaded', () => {
            loadSchema('operator');
        });
    </script>
</body>
</html>
```

- [ ] **Step 3: Commit**

```bash
git add static/index.html
git commit -m "feat: create responsive web UI with safe DOM manipulation"
```

---

## Phase 5: Testing & Integration

### Task 6: Full integration test

**Files:**
- No new files

- [ ] **Step 1: Install dependencies**

```bash
python -m pip install -q -r requirements.txt
```

- [ ] **Step 2: Reset database (remove old one if exists)**

```bash
rm -f manufacturing.db
python data_seed.py
```

Expected:
```
✓ Database created at manufacturing.db
```

- [ ] **Step 3: Start server in background**

```bash
python app.py > server.log 2>&1 &
sleep 3
```

- [ ] **Step 4: Test /tables endpoint (operator role)**

```bash
curl -s "http://localhost:8000/tables?user_role=operator" | python -m json.tool
```

Expected: JSON with "operator" accessible tables (production_orders, inventory)

- [ ] **Step 5: Test /tables endpoint (director role)**

```bash
curl -s "http://localhost:8000/tables?user_role=director" | python -m json.tool
```

Expected: JSON with all 5 tables accessible

- [ ] **Step 6: Test /ask endpoint with allowed query (operator)**

```bash
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me all production orders", "user_role": "operator"}' | python -m json.tool
```

Expected: Should return SQL, results, no error

- [ ] **Step 7: Test /ask endpoint with denied access (operator trying to query users)**

```bash
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "List all users and their roles", "user_role": "operator"}' | python -m json.tool
```

Expected: Should return error about access denied to users table

- [ ] **Step 8: Verify HTML is served**

```bash
curl -s "http://localhost:8000/" | head -20
```

Expected: HTML content starts with `<!DOCTYPE html>`

- [ ] **Step 9: Stop server**

```bash
pkill -f "python app.py"
sleep 1
```

- [ ] **Step 10: Commit final state**

```bash
git add -A
git commit -m "test: verify all components working end-to-end"
```

---

## Summary

Your POC now includes:

✅ **Database**: SQLite with 5 tables (products, parts, inventory, production_orders, users)  
✅ **Backend**: FastAPI server with Claude text-to-SQL integration  
✅ **Access Control**: 3 roles (Operator/Supervisor/Director) with table-level permissions  
✅ **Frontend**: Beautiful, responsive UI with role selector and real-time schema filtering  
✅ **Data**: Realistic manufacturing sample data  

To run it:
```bash
python app.py
# Visit http://localhost:8000
```

---

## Spec Coverage Check

| Spec Section | Implemented By |
|---|---|
| SQLite Database | Task 3 (data_seed.py) |
| Manufacturing Schema (4 tables) | Task 3 |
| Users table for roles | Task 3 |
| FastAPI Server | Task 4 (app.py) |
| Claude Integration | Task 4 |
| /tables endpoint | Task 4 |
| /ask endpoint | Task 4 |
| Access Control Utilities | Task 2 (utils/access_control.py) |
| Role-based filtering | Task 4 + Task 5 |
| HTML/JS Frontend | Task 5 (static/index.html) |
| Role selector dropdown | Task 5 |
| Schema browser | Task 5 |
| Results display | Task 5 |
| Integration testing | Task 6 |

All spec requirements covered. ✓
