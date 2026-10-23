from io import BytesIO
import pandas as pd
import pytest
from src.validation import DataError, read_upload, validate


def test_missing_required(raw):
    with pytest.raises(DataError, match='booking_value'):
        validate(raw.drop(columns='booking_value'))


def test_optional_absent(raw):
    result = validate(raw[['booking_id', 'booking_date', 'status', 'booking_value']])
    assert len(result.accepted) == 4
    assert result.accepted.cost.isna().all()
    assert result.accepted.channel.eq('Unknown').all()


@pytest.mark.parametrize('column,value', [
    ('booking_id', None), ('booking_id', ' '), ('booking_date', '31/01/2025'),
    ('booking_date', '2025-02-30'), ('booking_date', 'garbage'),
    ('booking_value', -1), ('booking_value', 'oops'), ('booking_value', float('inf')),
    ('booking_value', None), ('status', 'unexpected'), ('status', None),
])
def test_invalid_required_quarantined(raw, column, value):
    raw[column] = raw[column].astype(object)
    raw.loc[0, column] = value
    result = validate(raw)
    assert result.summary['quarantined_rows'] == 1
    assert result.accepted.booking_id.tolist() == ['B', 'C', 'D']
    assert result.issues.source_row.iloc[0] == 2


def test_missing_and_invalid_optional_logged(raw):
    raw.loc[0, 'channel'] = None
    raw.loc[0, 'cost'] = -1
    raw.loc[0, 'star_rating'] = 6
    result = validate(raw)
    assert len(result.accepted) == 4
    assert result.accepted.loc[0, 'channel'] == 'Unknown'
    assert pd.isna(result.accepted.loc[0, 'cost'])
    assert len(result.issues) == 3


def test_exact_duplicate(raw):
    result = validate(pd.concat([raw, raw.iloc[[0]]], ignore_index=True))
    assert result.summary['duplicate_rows'] == 1
    assert len(result.accepted) == 4


def test_conflicting_ids(raw):
    raw.loc[1, 'booking_id'] = 'A'
    result = validate(raw)
    assert result.summary['conflicting_rows'] == 2
    assert result.accepted.booking_id.tolist() == ['C', 'D']


def test_aliases_and_status_normalization(raw):
    raw = raw.rename(columns={'booking_id': 'Reservation ID', 'booking_value': 'Selling Price', 'status': 'Booking Status'})
    raw.loc[1, 'Booking Status'] = 'canceled'
    assert validate(raw).accepted.loc[1, 'status'] == 'Cancelled'


def test_ambiguous_columns(raw):
    raw['selling_price'] = 10
    with pytest.raises(DataError, match='same field'):
        validate(raw)


def test_personal_information_excluded(raw):
    raw['guest_email'] = 'private@example.com'
    result = validate(raw)
    assert 'guest_email' not in result.accepted
    assert result.summary['ignored_columns'] == ['guest_email']
    assert 'private@example.com' not in result.issues.to_json()


@pytest.mark.parametrize('content,name', [(b'bad', 'x.pdf'), (b'', 'x.csv'), (b'bad', 'x.xlsx'),
                                          (b'a,b\n', 'x.csv'), (b'\xff', 'x.csv')])
def test_malformed_uploads(content, name):
    with pytest.raises(DataError):
        read_upload(content, name)


def test_csv_and_excel(raw):
    assert len(read_upload(raw.to_csv(index=False).encode(), 'bookings.csv')) == 4
    output = BytesIO()
    raw.to_excel(output, index=False)
    assert len(read_upload(output.getvalue(), 'bookings.xlsx')) == 4


def test_empty_frame_with_headers(raw):
    result = validate(raw.iloc[:0])
    assert result.accepted.empty
    assert result.summary['input_rows'] == 0
