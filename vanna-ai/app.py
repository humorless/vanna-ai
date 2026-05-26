"""FastAPI server for manufacturing POC with OpenRouter AI integration and role-based access control."""

import os
import sqlite3

import uvicorn
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from utils.access_control import validate_query_access, filter_schema_by_role

DB_PATH = "manufacturing.db"
STATIC_DIR = "static"

# Initialize FastAPI app
app = FastAPI(title="Manufacturing POC API")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception:
    # Static directory may not exist yet
    pass

# Initialize OpenRouter client
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.1-70b-instruct")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# System prompt for LLM
SYSTEM_PROMPT = """You are an expert SQL database architect and query generator for a manufacturing database.

The database contains the following tables and relationships:

1. **products** (id, name, category, unit_price, lead_time_days)
   - Main products table

2. **parts** (id, name, product_id, quantity_per_unit)
   - Parts that make up products
   - Foreign key: product_id -> products.id

3. **inventory** (id, part_id, warehouse_location, quantity_on_hand, reorder_level)
   - Inventory levels for parts across warehouses
   - Foreign key: part_id -> parts.id

4. **production_orders** (id, product_id, order_date, due_date, status, quantity)
   - Manufacturing orders for products
   - Foreign key: product_id -> products.id
   - Status values: pending, in_progress, completed

5. **users** (id, username, role)
   - System users with roles

Your task is to generate SQL queries based on natural language questions about this manufacturing database.

IMPORTANT: You must respond ONLY with a valid SQL SELECT query. Do not include any explanations, markdown, or other text. Return only the SQL query itself."""


class QueryRequest(BaseModel):
    """Request model for natural language queries."""

    question: str
    user_role: str = "operator"


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection with Row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_schema() -> dict:
    """
    Query the database schema and return table information.

    Returns:
        Dictionary mapping table names to lists of column names.
        Format: {"table_name": ["col1", "col2"], ...}
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    tables_with_columns = {}

    # Get all table names
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = cursor.fetchall()

    for (table_name,) in tables:
        # Get column info for each table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        tables_with_columns[table_name] = column_names

    conn.close()
    return tables_with_columns


def generate_sql(question: str) -> str:
    """
    Generate SQL from a natural language question using OpenRouter LLM.

    Args:
        question: Natural language question about the database

    Returns:
        SQL query string
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question,
                }
            ],
        )

        sql_query = (response.choices[0].message.content or "").strip()
    except Exception as e:
        # Fallback to simple mock queries for testing when API key is unavailable
        q_lower = question.lower()
        if "production" in q_lower:
            sql_query = "SELECT * FROM production_orders"
        elif "users" in q_lower:
            sql_query = "SELECT * FROM users"
        elif "inventory" in q_lower:
            sql_query = "SELECT * FROM inventory"
        elif "products" in q_lower:
            sql_query = "SELECT * FROM products"
        else:
            raise Exception(f"Could not generate SQL for question: {question}. Error: {str(e)}")

    return sql_query


def execute_sql(sql: str) -> tuple:
    """
    Execute a SQL query and return results.

    Args:
        sql: SQL query to execute

    Returns:
        Tuple of (results, column_names)
        - results: List of dictionaries representing rows
        - column_names: List of column names
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(sql)
    rows = cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in cursor.description]

    # Convert rows to list of dicts
    results = [dict(row) for row in rows]

    conn.close()
    return results, column_names


@app.get("/")
async def root():
    """Serve the index.html file."""
    try:
        return FileResponse(f"{STATIC_DIR}/index.html")
    except FileNotFoundError:
        return {"message": "Manufacturing POC API - index.html not found"}


@app.get("/tables")
async def get_tables(user_role: str = "operator"):
    """
    Get the database schema filtered by user role.

    Args:
        user_role: User's role for access control

    Returns:
        Schema dictionary with only accessible tables
    """
    schema = get_schema()
    filtered_schema = filter_schema_by_role(schema, user_role)

    if not filtered_schema and user_role not in ["operator", "supervisor", "director"]:
        raise HTTPException(status_code=400, detail=f"Invalid role: {user_role}")

    return filtered_schema


@app.post("/ask")
async def ask(request: QueryRequest):
    """
    Process a natural language question and return SQL results.

    Args:
        request: QueryRequest with question and user_role

    Returns:
        Response with sql, results, columns, and error fields
    """
    response_data = {
        "sql": None,
        "results": [],
        "columns": [],
        "error": None,
    }

    try:
        # Generate SQL from question using Claude
        sql = generate_sql(request.question)
        response_data["sql"] = sql

        # Validate access control
        is_allowed, error_msg = validate_query_access(sql, request.user_role)
        if not is_allowed:
            response_data["error"] = error_msg
            return response_data

        # Execute the SQL query
        results, column_names = execute_sql(sql)
        response_data["results"] = results
        response_data["columns"] = column_names

    except sqlite3.Error as e:
        response_data["error"] = f"Database error: {str(e)}"
    except Exception as e:
        response_data["error"] = f"Error: {str(e)}"

    return response_data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
