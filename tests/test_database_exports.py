from io import BytesIO
import pandas as pd
import pytest
from src.database import datasets, initialize, load_dataset, quality_report, reset_demo, save_dataset
from src.exports import csv_bytes, excel_bytes, summary_frame
from src.analytics import filter_bookings
from src.validation import validate


def test_database_round_trip_and_idempotency(tmp_path, raw):
    db = tmp_path / 'test.db'
    initialize(db)
    initialize(db)
    result = validate(raw)
    dataset_id, created = save_dataset(db, result, "O'Brien dataset")
    assert created
    assert len(load_dataset(db, dataset_id)) == 4
    assert save_dataset(db, result, 'renamed.csv') == (dataset_id, False)
    assert save_dataset(db, validate(raw.iloc[::-1]), 'reordered.csv') == (dataset_id, False)
    assert len(datasets(db)) == 1
    assert quality_report(db, dataset_id)[0]['accepted_rows'] == 4


def test_demo_reset_requires_confirmation_preserves_uploads(tmp_path, raw):
    db = tmp_path / 'test.db'
    initialize(db)
    demo, _ = save_dataset(db, validate(raw), 'Demo', is_demo=True)
    uploaded, _ = save_dataset(db, validate(raw), 'User data')
    with pytest.raises(ValueError):
        reset_demo(db, '')
    assert len(datasets(db)) == 2
    reset_demo(db, 'RESET DEMO')
    assert datasets(db).id.tolist() == [uploaded]
    assert len(load_dataset(db, uploaded)) == 4
    assert load_dataset(db, demo).empty


def test_audit_persists(tmp_path, raw):
    raw.loc[0, 'booking_value'] = -10
    db = tmp_path / 'test.db'
    initialize(db)
    dataset_id, _ = save_dataset(db, validate(raw), 'Bad row')
    summary, issues, rejected = quality_report(db, dataset_id)
    assert summary['quarantined_rows'] == 1
    assert issues.source_row.tolist() == [2]
    assert rejected.booking_id.tolist() == ['A']


def test_no_empty_import(tmp_path, raw):
    db = tmp_path / 'test.db'
    initialize(db)
    with pytest.raises(ValueError, match='No accepted'):
        save_dataset(db, validate(raw.iloc[:0]), 'Empty')


def test_filtered_csv_and_summary(clean):
    selected = filter_bookings(clean, selections={'channel': ['Direct']})
    exported = pd.read_csv(BytesIO(csv_bytes(selected)))
    assert exported.booking_id.tolist() == ['A', 'C']
    summary = summary_frame(selected).set_index('name')
    assert summary.loc['Total bookings', 'value'] == 2
    assert summary.loc['Total booking value', 'value'] == 400
    workbook = pd.read_excel(BytesIO(excel_bytes(selected)), sheet_name=None)
    assert set(workbook) == {'Summary', 'Filtered bookings'}
    assert len(workbook['Filtered bookings']) == 2


def test_csv_formula_neutralization(clean):
    clean.loc[0, 'city'] = '=1+1'
    exported = pd.read_csv(BytesIO(csv_bytes(clean)))
    assert exported.loc[0, 'city'] == "'=1+1"
