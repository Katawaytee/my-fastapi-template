from typing import Dict
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.expression import ColumnElement


def build_sort_expression(
    order_by: str, valid_columns: Dict[str, ColumnElement], default_field: str
) -> UnaryExpression:
    """
    Build a database sort expression based on an input string.

    Parameters
    ----------
    - `order_by` (str)
        The raw sort string (e.g., "studentid desc", "name asc").
    - `valid_columns` (Dict[str, ColumnElement])
        A dictionary mapping allowed string keys to their actual SQLAlchemy
        columns or expressions.
    - `default_field` (str)
        The fallback field key to use if the input is invalid or missing.

    Returns
    -------
    **UnaryExpression**
    - The generated SQL sort condition (e.g., table.c.col.desc()).
    """

    # Safely handle None or empty strings
    safe_order_by = (order_by or "").strip().lower()
    parts = safe_order_by.split()

    sort_field = parts[0] if parts else default_field
    sort_direction = parts[1] if len(parts) > 1 else "asc"

    sort_col = valid_columns.get(sort_field)
    if sort_col is None:
        sort_col = valid_columns.get(default_field)

    if sort_col is None:
        raise ValueError(f"Default field '{default_field}' is not in valid_columns.")

    if sort_direction == "desc":
        return sort_col.desc()

    return sort_col.asc()
