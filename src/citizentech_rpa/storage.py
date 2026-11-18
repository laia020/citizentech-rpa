"""Estado local durável; lock exclusivo impede dois lotes com a mesma base."""

import fcntl
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def open_state(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(str(path) + ".lock", "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("estado_em_uso") from None
        connection = None
        try:
            connection = sqlite3.connect(path)
            os.chmod(path, 0o600)
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("""CREATE TABLE IF NOT EXISTS occurrences (
                mode TEXT NOT NULL, id TEXT NOT NULL, fingerprint TEXT NOT NULL,
                status TEXT NOT NULL, result TEXT, PRIMARY KEY (mode, id)
            )""")
            connection.commit()
            yield connection
        finally:
            if connection is not None:
                connection.close()
            fcntl.flock(lock, fcntl.LOCK_UN)


def lookup(connection, mode, identifier):
    row = connection.execute(
        "SELECT fingerprint, status, result FROM occurrences WHERE mode=? AND id=?",
        (mode, identifier),
    ).fetchone()
    if row is None:
        return None
    return {"fingerprint": row[0], "status": row[1], "result": json.loads(row[2]) if row[2] else None}


def save(connection, mode, identifier, fingerprint, status, result=None):
    connection.execute(
        """INSERT INTO occurrences(mode, id, fingerprint, status, result) VALUES(?,?,?,?,?)
        ON CONFLICT(mode,id) DO UPDATE SET status=excluded.status, result=excluded.result""",
        (mode, identifier, fingerprint, status, json.dumps(result, ensure_ascii=False) if result else None),
    )
    connection.commit()
