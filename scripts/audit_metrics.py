"""Read-only independent Decimal reconciliation of each stored snapshot."""
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from src.analytics import kpis


def audit(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    reports = []
    try:
        for dataset in db.execute('SELECT id, name, currency FROM datasets ORDER BY id'):
            records = db.execute('SELECT * FROM bookings WHERE dataset_id=?', (dataset['id'],)).fetchall()
            rows = [dict(row) for row in records]
            if not rows:
                reports.append({'dataset_id': dataset['id'], 'empty': True})
                continue
            n = len(rows)
            cancelled = sum(row['status'] == 'Cancelled' for row in rows)
            retained = [row for row in rows if row['status'] in ('Confirmed', 'Completed')]
            total = sum((Decimal(str(row['booking_value'])) for row in rows), Decimal(0))
            retained_value = sum((Decimal(str(row['booking_value'])) for row in retained), Decimal(0))
            markup = sum((Decimal(str(row['booking_value'])) - Decimal(str(row['cost'])) for row in retained), Decimal(0)) if retained and all(row['cost'] is not None for row in retained) else None
            independent = {
                'Total bookings': Decimal(n),
                'Confirmed bookings': Decimal(sum(row['status'] == 'Confirmed' for row in rows)),
                'Cancelled bookings': Decimal(cancelled),
                'Cancellation rate': Decimal(cancelled) / Decimal(n),
                'Total booking value': total,
                'Retained booking value': retained_value,
                'Average booking value': total / Decimal(n),
                'Retained markup': markup,
            }
            actual = kpis(pd.DataFrame(rows))
            matches = {name: actual[name] is None if value is None else
                       actual[name] is not None and abs(Decimal(str(actual[name])) - value) < Decimal('0.000001')
                       for name, value in independent.items()}
            reports.append({'dataset_id': dataset['id'], 'name': dataset['name'], 'currency': dataset['currency'],
                            'retained_count': len(retained), 'cost_known_retained': sum(row['cost'] is not None for row in retained),
                            'independent_metrics': {name: str(value) if value is not None else None for name, value in independent.items()},
                            'matches': matches})
        return {'integrity_check': db.execute('PRAGMA integrity_check').fetchone()[0],
                'foreign_key_violations': len(db.execute('PRAGMA foreign_key_check').fetchall()), 'datasets': reports}
    finally:
        db.close()


if __name__ == '__main__':
    report = audit(ROOT / 'data' / 'bookings.db')
    print(json.dumps(report, indent=2))
    if report['integrity_check'] != 'ok' or report['foreign_key_violations'] or any(
            not all(item.get('matches', {}).values()) for item in report['datasets']):
        raise SystemExit(1)
