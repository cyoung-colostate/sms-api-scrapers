from __future__ import annotations
import logging
from typing import Optional, Sequence, Dict, Any, Literal, Optional
from sqlalchemy import text, inspect, bindparam
from db import engine
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

logger = logging.getLogger(__name__)

_PREFERRED_ORDER_COLS: Sequence[str] = (
    "updated",     
    "created",     
    "irrimax_save",    
    "groguru_save",
    "irrimax_pull",
    "groguru_pull",
    "id",             # fallback
)

def _existing_columns(table: str) -> set[str]:
    try:
        insp = inspect(engine)
        return {c["name"] for c in insp.get_columns(table)}
    except Exception as e:
        logger.error("Failed to inspect table %s: %r", table, e)
        return set()

def get_last_sensor_pull(
    source: Optional[str] = None,
    order_preference: Sequence[str] = _PREFERRED_ORDER_COLS,
) -> Optional[Dict[str, Any]]:
    """
    Fetch the most recent row from sensor_pulls.
    If `source` is provided and the table has a 'source' column, it filters by it.
    Orders by the first existing columns in `order_preference` (DESC).
    """
    table = "sensor_pulls"
    cols = _existing_columns(table)
    if not cols:
        return None

    order_cols = [c for c in order_preference if c in cols] or (["id"] if "id" in cols else [])
    if not order_cols:
        # last resort: pick any existing column name deterministically
        order_cols = [sorted(cols)[0]]

    where_clause = ""
    params: Dict[str, Any] = {}
    if source and "source" in cols:
        where_clause = "WHERE source = :source"
        params["source"] = source

    order_clause = ", ".join(f"{c} DESC NULLS LAST" for c in order_cols)
    sql = f"SELECT * FROM {table} {where_clause} ORDER BY {order_clause} LIMIT 1"

    try:
        with engine.begin() as conn:
            row = conn.execute(text(sql), params).mappings().first()
            return dict(row) if row else None
    except Exception as e:
        logger.error("get_last_sensor_pull failed: %r", e)
        return None

def get_last_window_end(source: Optional[str] = None):
    """
    Return best-guess 'last cutoff' from the latest row:
    tries window_end, then pulled_at, created_at, updated_at, ts.
    """
    row = get_last_sensor_pull(source=source)
    if not row:
        return None
    for key in _PREFERRED_ORDER_COLS:
        if key in row and row[key] is not None:
            return row[key]
    return None

_STEP_COLS = {
    "irrimax": {"pull": "irrimax_pull", "save": "irrimax_save"},
    "groguru": {"pull": "groguru_pull", "save": "groguru_save"},
}

def begin_sensor_pull_run() -> str:
    """
    Insert a new row and return its id. Assumes 'id' and 'created' default
    are handled by the DB (uuid, now()).
    """
    sql = text("INSERT INTO sensor_pulls DEFAULT VALUES RETURNING id")
    with engine.begin() as conn:
        row = conn.execute(sql).mappings().first()
        return str(row["id"])

_STEP_COLS = {
    "irrimax": {"pull": "irrimax_pull", "save": "irrimax_save"},
    "groguru": {"pull": "groguru_pull", "save": "groguru_save"},
}

def begin_sensor_pull_run() -> uuid.UUID:
    sql = text("INSERT INTO sensor_pulls DEFAULT VALUES RETURNING id")
    with engine.begin() as conn:
        row = conn.execute(sql).mappings().first()
        # return a real UUID object so downstream binds are typed correctly
        return row["id"]  # psycopg2 already returns uuid.UUID for uuid columns

def mark_step_done(
    run_id: uuid.UUID,        
    source: Literal["irrimax", "groguru"],
    step: Literal["pull", "save"],
) -> None:
    col = _STEP_COLS[source][step]     # safe column pick

    sql = (
        text(f"UPDATE sensor_pulls SET {col} = CURRENT_TIMESTAMP "
             "WHERE id = :id")
        .bindparams(bindparam("id", type_=PG_UUID)) 
    )

    with engine.begin() as conn:
        res = conn.execute(sql, {"id": run_id})
        if res.rowcount != 1:
            # Loud, actionable signal when nothing was written
            raise RuntimeError(
                f"mark_step_done affected {res.rowcount} rows for id={run_id}, "
                f"source={source}, step={step} (expected 1)"
            )
        
def debug_peek(run_id):
    sql = text("""
        SELECT irrimax_pull, irrimax_save, groguru_pull, groguru_save
        FROM sensor_pulls WHERE id = :id
    """).bindparams(bindparam("id", type_=PG_UUID))
    with engine.begin() as conn:
        row = conn.execute(sql, {"id": run_id}).mappings().first()
        logger.info("Row now: %s", row)