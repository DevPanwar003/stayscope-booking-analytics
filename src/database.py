"""Atomic snapshot imports. No cross-dataset aggregation or silent replacement."""
from contextlib import contextmanager
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import sqlite3

import pandas as pd


@contextmanager
def connection(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    db.execute('PRAGMA foreign_keys=ON')
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path):
    with connection(path) as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY, fingerprint TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL, currency TEXT NOT NULL, is_demo INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                quality_json TEXT NOT NULL, issues_json TEXT NOT NULL, rejected_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS bookings (
                dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
                booking_id TEXT NOT NULL, booking_date TEXT NOT NULL,
                status TEXT NOT NULL, booking_value REAL NOT NULL CHECK(booking_value >= 0),
                city TEXT, property TEXT, channel TEXT, room_type TEXT,
                star_rating REAL, cost REAL, source_row INTEGER,
                PRIMARY KEY(dataset_id, booking_id)
            );
            CREATE INDEX IF NOT EXISTS booking_dates ON bookings(dataset_id, booking_date);
        ''')


def save_dataset(path, result, name, currency='INR', is_demo=False):
    with connection(path) as db:
        # Serialize fingerprint lookup + insertion, including simultaneous imports.
        db.execute('BEGIN IMMEDIATE')
        return _save_dataset(db, result, name, currency, is_demo)


def _save_dataset(db, result, name, currency='INR', is_demo=False):
    """Insert within the caller's transaction (also used by atomic demo restore)."""
    if result.accepted.empty:
        raise ValueError('No accepted rows to import.')
    data = result.accepted
    # Row order and original line numbers do not change snapshot identity.
    canonical = data.drop(columns='source_row').sort_values('booking_id').to_csv(index=False)
    audit_identity = json.dumps(result.summary, sort_keys=True)
    fingerprint = sha256((currency + str(is_demo) + canonical + audit_identity).encode()).hexdigest()
    issues_json = result.issues.to_json(orient='records')
    rejected_json = result.rejected.to_json(orient='records', date_format='iso')
    existing = db.execute('SELECT id, issues_json, rejected_json FROM datasets WHERE fingerprint=?', (fingerprint,)).fetchone()
    if existing:
        if json.loads(existing[1]) == json.loads(issues_json) and json.loads(existing[2]) == json.loads(rejected_json):
            return existing[0], False
        # Preserve the original fingerprint for backwards compatibility, while
        # distinguishing changed quarantine evidence even if counts are equal.
        detail = json.dumps([json.loads(issues_json), json.loads(rejected_json)], sort_keys=True)
        fingerprint = sha256((fingerprint + detail).encode()).hexdigest()
        existing = db.execute('SELECT id FROM datasets WHERE fingerprint=?', (fingerprint,)).fetchone()
        if existing:
            return existing[0], False
    cursor = db.execute('''INSERT INTO datasets
        (fingerprint, name, currency, is_demo, quality_json, issues_json, rejected_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (fingerprint, name, currency, int(is_demo), json.dumps(result.summary),
         issues_json, rejected_json))
    dataset_id = cursor.lastrowid
    columns = ['booking_id', 'booking_date', 'status', 'booking_value', 'city',
               'property', 'channel', 'room_type', 'star_rating', 'cost', 'source_row']
    stored = data[columns].copy()
    stored['booking_date'] = stored.booking_date.dt.strftime('%Y-%m-%d')
    stored = stored.astype(object).where(pd.notna(stored), None)
    db.executemany('INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   [(dataset_id, *row) for row in stored.itertuples(index=False, name=None)])
    return dataset_id, True


def datasets(path):
    with connection(path) as db:
        return pd.read_sql_query('SELECT id, name, currency, is_demo, created_at FROM datasets ORDER BY id DESC', db)


def load_dataset(path, dataset_id):
    with connection(path) as db:
        data = pd.read_sql_query('SELECT * FROM bookings WHERE dataset_id=?', db, params=(int(dataset_id),))
    data['booking_date'] = pd.to_datetime(data.booking_date)
    return data.drop(columns='dataset_id')


def quality_report(path, dataset_id):
    with connection(path) as db:
        row = db.execute('SELECT quality_json, issues_json, rejected_json FROM datasets WHERE id=?',
                         (int(dataset_id),)).fetchone()
    if row is None:
        raise ValueError('Dataset not found.')
    return json.loads(row[0]), pd.read_json(StringIO(row[1]), dtype=False), pd.read_json(StringIO(row[2]), dtype=False)


def reset_demo(path, confirmation, replacement=None):
    if confirmation != 'RESET DEMO':
        raise ValueError('Type RESET DEMO to confirm.')
    with connection(path) as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('DELETE FROM datasets WHERE is_demo=1')
        if replacement is not None:
            # Any insertion failure rolls back the deletion as well.
            return _save_dataset(db, replacement, 'Synthetic hotel demonstration', is_demo=True)
