"""
Manage SQLite according to Singleton pattern.

Why use Singleton here:
- All repository needs to share the same database connection
so that transactions can be managed properly and consistent
- If each repostory has its own connection, it will be hard to
manage transactions across many tables, and abundant open and close connection
- DatabaseConnection() anywhere in the code will always return one instance
(use __new__ to control the creation of instance)

"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from src.config.settings import settings
from src.exceptions import DatabaseOperationError


class DatabaseConnection:
    _instance: "DatabaseConnection | None" = None
    _connection: sqlite3.Connection | None = None

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_connection(self) -> sqlite3.Connection:
        """Lazy-connect: open connection when first time use"""
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(settings.database_path)
                self._connection.execute("PRAGMA foreign_keys = ON")
                self._connection.row_factory = sqlite3.Row
            except sqlite3.Error as exc:
                raise DatabaseOperationError(f"Failed to connect to database: {exc}") from exc
        return self._connection

    @contextmanager
    def get_cursor(self, commit: bool = False) -> Iterator[sqlite3.Cursor]:
        """Context manager provide cursor, close cursor when error.

        commit=True: use for INSERT/UPDATE/DELETE not batch, auto commit
        if command executed successfully, rollback if there is exception
        commit=False (default): use for SELECT, no need commit.
        """
        connection = self._get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        except sqlite3.Error as exc:
            connection.rollback()
            raise DatabaseOperationError(f"Database operation failed: {exc}") from exc
        finally:
            cursor.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Cursor]:
        """Context manager for transactions many steps (create Order with many
        OrderItem, update Product.

        All commands in the block will be shared 1 cursor and only
        commit 1 TIME at the end of the block if all commands executed successfully;
        rollback if there is any error in the block
        """
        connection = self._get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except sqlite3.Error as exc:
            connection.rollback()
            raise DatabaseOperationError(f"Database operation failed: {exc}") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    def execute_write(self, query: str, params: tuple[Any, ...] = (), commit: bool = True) -> int:
        """
        Execure INSERT/UPDATE/DELETE command safe (parameterized query)

        Return lastrowid (good for INSERT to get id just created)
        NOT connect user input into query - always pass through params
        """
        with self.get_cursor(commit=commit) as cursor:
            cursor.execute(query, params)
            lastrowid = cursor.lastrowid
            return 0 if lastrowid is None else lastrowid

    def execute_many(
        self, query: str, params_list: list[tuple[Any, ...]], commit: bool = True
    ) -> None:
        """
        Execute many INSERT/UPDATE/DELETE command
        """
        with self.get_cursor(commit=commit) as cursor:
            cursor.executemany(query, params_list)

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        """
        Execute SELECT, return all results
        """
        with self.get_cursor(commit=False) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        """
        Execute SELECT, return one result or None if no result
        """
        with self.get_cursor(commit=False) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_script(self, script_sql: str) -> None:
        """
        Execute multiple SQL commands in one script
        (use for init_db and file .sql)
        """
        connection = self._get_connection()
        try:
            connection.executescript(script_sql)
            connection.commit()
        except sqlite3.Error as exc:
            connection.rollback()
            raise DatabaseOperationError(f"Database operation failed: {exc}") from exc

    def close(self) -> None:
        """Close the database connection"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
