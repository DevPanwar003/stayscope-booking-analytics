"""Idempotently initialize SQLite and import the supplied demo."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.database import initialize, save_dataset
from src.validation import read_upload, validate

if __name__ == '__main__':
    db = ROOT / 'data' / 'bookings.db'
    sample = ROOT / 'data' / 'sample_hotel_bookings.csv'
    initialize(db)
    dataset_id, created = save_dataset(db, validate(read_upload(sample.read_bytes(), sample.name)),
                                      'Synthetic hotel demonstration', is_demo=True)
    print(f'Database ready: {db}; demo ID={dataset_id}; new import={created}')
