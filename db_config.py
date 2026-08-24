import os
from threading import Lock

from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool


_pool = None
_pool_lock = Lock()


def _get_required_env(name):
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


def _create_pool():
    return MySQLConnectionPool(
        pool_name=os.getenv("DB_POOL_NAME", "anime_pool"),
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        host=_get_required_env("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=_get_required_env("DB_USER"),
        password=_get_required_env("DB_PASSWORD"),
        database=_get_required_env("DB_NAME"),
        autocommit=False,
        connection_timeout=10,
        read_timeout=10,
        write_timeout=10,
        pool_reset_session=False,
    )


def _reset_pool():
    global _pool

    if _pool is not None:
        try:
            _pool._remove_connections()
        except Error:
            pass
    _pool = None


def connect():
    global _pool

    with _pool_lock:
        if _pool is None:
            _pool = _create_pool()

        try:
            return _pool.get_connection()
        except Error:
            _reset_pool()
            try:
                _pool = _create_pool()
                return _pool.get_connection()
            except Error as exc:
                raise RuntimeError(
                    "Unable to connect to the MySQL database."
                ) from exc