import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text


def get_database_url() -> str | None:
    return st.secrets.get("NEON_DATABASE_URL") or os.getenv("NEON_DATABASE_URL")


def get_engine():
    db_url = get_database_url()
    if not db_url:
        return None
    return create_engine(db_url, future=True)


def ensure_actions_table(engine) -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS actions (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        owner TEXT,
        due_date DATE,
        status TEXT,
        commodity TEXT,
        country_iso3 TEXT,
        expected_risk_impact TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT now(),
        updated_at TIMESTAMP DEFAULT now()
    );
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))


def list_actions(engine) -> pd.DataFrame:
    query = "SELECT * FROM actions ORDER BY created_at DESC"
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn)


def insert_action(engine, payload: dict) -> None:
    query = text(
        """
        INSERT INTO actions (title, owner, due_date, status, commodity, country_iso3, expected_risk_impact, notes)
        VALUES (:title, :owner, :due_date, :status, :commodity, :country_iso3, :expected_risk_impact, :notes)
        """
    )
    with engine.begin() as conn:
        conn.execute(query, payload)


def update_action_status(engine, action_id: int, status: str) -> None:
    query = text("UPDATE actions SET status=:status, updated_at=now() WHERE id=:id")
    with engine.begin() as conn:
        conn.execute(query, {"status": status, "id": action_id})


def delete_action(engine, action_id: int) -> None:
    query = text("DELETE FROM actions WHERE id=:id")
    with engine.begin() as conn:
        conn.execute(query, {"id": action_id})
