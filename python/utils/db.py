"""
PAYMENTIQ Database Utility
Manages connections and transactions for PostgreSQL and DuckDB analytical storage engines.
"""
import os
from pathlib import Path
from typing import Optional, Any
import duckdb
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

from python.utils.logger import setup_logger

load_dotenv()
logger = setup_logger("db_manager")

class DatabaseManager:
    """Centralized database connection and query execution manager."""

    def __init__(self):
        self.pg_host = os.getenv("DB_HOST", "127.0.0.1")
        self.pg_port = os.getenv("DB_PORT", "5433")
        self.pg_name = os.getenv("DB_NAME", "paymentiq_dw")
        self.pg_user = os.getenv("DB_USER", "postgres")
        self.pg_pass = os.getenv("DB_PASSWORD", "paymentiq_secure_dev_password")
        self.duckdb_path = os.getenv("DUCKDB_PATH", "data/processed/paymentiq.duckdb")

        self._pg_engine: Optional[Engine] = None
        self._duckdb_conn: Optional[duckdb.DuckDBPyConnection] = None

    @property
    def pg_url(self) -> str:
        """Constructs SQLAlchemy connection URI for PostgreSQL."""
        return f"postgresql+psycopg://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_name}"

    def get_pg_engine(self) -> Engine:
        """Returns or initializes the SQLAlchemy engine for PostgreSQL."""
        if self._pg_engine is None:
            self._pg_engine = create_engine(
                self.pg_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            logger.info("Initialized PostgreSQL connection pool on port %s", self.pg_port)
        return self._pg_engine

    def get_duckdb(self) -> duckdb.DuckDBPyConnection:
        """Returns or initializes DuckDB analytical connection."""
        if self._duckdb_conn is None:
            Path(self.duckdb_path).parent.mkdir(parents=True, exist_ok=True)
            self._duckdb_conn = duckdb.connect(self.duckdb_path)
            logger.info("Connected to DuckDB database at %s", self.duckdb_path)
        return self._duckdb_conn

    def test_connections(self) -> dict[str, bool]:
        """Verifies active connectivity to both database backends."""
        results = {"postgresql": False, "duckdb": False}
        try:
            engine = self.get_pg_engine()
            with engine.connect() as conn:
                val = conn.execute(text("SELECT 1")).scalar()
                results["postgresql"] = (val == 1)
        except Exception as e:
            logger.warning("PostgreSQL connection check failed: %s", e)

        try:
            ddb = self.get_duckdb()
            val = ddb.execute("SELECT 1").fetchone()[0]
            results["duckdb"] = (val == 1)
        except Exception as e:
            logger.warning("DuckDB connection check failed: %s", e)

        return results

db_manager = DatabaseManager()
