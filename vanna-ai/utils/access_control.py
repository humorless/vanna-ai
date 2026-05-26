"""Role-based access control utilities for manufacturing POC."""

import re
from typing import Dict, List, Tuple

# Role-to-permissions mapping
ROLE_PERMISSIONS = {
    "operator": ["production_orders", "inventory"],
    "supervisor": ["production_orders", "inventory", "products"],
    "director": ["products", "parts", "inventory", "production_orders", "users"],
}

# Valid roles
VALID_ROLES = list(ROLE_PERMISSIONS.keys())


def validate_query_access(sql: str, user_role: str) -> Tuple[bool, str]:
    """
    Validate if a user can execute a query based on their role.

    Args:
        sql: SQL query string to validate
        user_role: User's role (must be in VALID_ROLES)

    Returns:
        Tuple of (is_allowed: bool, error_message: str)
        - is_allowed: True if query is allowed, False otherwise
        - error_message: Empty string if allowed, error message if denied
    """
    # Validate role
    if user_role not in VALID_ROLES:
        return False, f"Invalid role: {user_role}. Valid roles: {', '.join(VALID_ROLES)}"

    # Get allowed tables for this role
    allowed_tables = set(ROLE_PERMISSIONS[user_role])

    # Extract table names from SQL query
    # Match common SQL patterns: FROM table_name, JOIN table_name, INSERT INTO table_name, UPDATE table_name, DELETE FROM table_name
    table_patterns = [
        r"FROM\s+(\w+)",
        r"JOIN\s+(\w+)",
        r"INTO\s+(\w+)",
        r"UPDATE\s+(\w+)",
        r"DELETE\s+FROM\s+(\w+)",
    ]

    referenced_tables = set()
    for pattern in table_patterns:
        matches = re.finditer(pattern, sql, re.IGNORECASE)
        for match in matches:
            referenced_tables.add(match.group(1).lower())

    # Check if all referenced tables are allowed
    unauthorized_tables = referenced_tables - allowed_tables
    if unauthorized_tables:
        return (
            False,
            f"Access denied. User role '{user_role}' cannot access table(s): {', '.join(sorted(unauthorized_tables))}. "
            f"Allowed tables: {', '.join(sorted(allowed_tables))}",
        )

    return True, ""


def filter_schema_by_role(
    tables_with_columns: Dict[str, List[str]], user_role: str
) -> Dict[str, List[str]]:
    """
    Filter schema to only include accessible tables for the user's role.

    Args:
        tables_with_columns: Dictionary mapping table names to lists of column names
                            Format: {"table_name": ["col1", "col2"], ...}
        user_role: User's role (must be in VALID_ROLES)

    Returns:
        Filtered dictionary containing only tables accessible to the user's role
        Empty dict if role is invalid

    Example:
        >>> schema = {"products": ["id", "name"], "inventory": ["id", "qty"], "users": ["id", "email"]}
        >>> filter_schema_by_role(schema, "operator")
        {"inventory": ["id", "qty"]}
    """
    # Validate role
    if user_role not in VALID_ROLES:
        return {}

    # Get allowed tables for this role
    allowed_tables = set(ROLE_PERMISSIONS[user_role])

    # Filter and return only accessible tables
    filtered_schema = {
        table: columns
        for table, columns in tables_with_columns.items()
        if table.lower() in allowed_tables
    }

    return filtered_schema
