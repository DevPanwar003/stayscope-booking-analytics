"""Generate only into a new path; never replace an existing data file."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.sample import generate_sample

if __name__ == '__main__':
    target = ROOT / 'data' / 'sample_hotel_bookings.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f'Preserved existing file: {target}')
    else:
        generate_sample().to_csv(target, index=False)
        print(f'Created 1,800 synthetic demo bookings: {target}')
