"""Explicit, auditable cleaning. Invalid required values quarantine the row."""
from dataclasses import dataclass
from io import BytesIO, StringIO
import csv
import re

import numpy as np
import pandas as pd

REQUIRED = ['booking_id', 'booking_date', 'status', 'booking_value']
DIMENSIONS = ['city', 'property', 'channel', 'room_type']
OPTIONAL = DIMENSIONS + ['star_rating', 'cost']
ALIASES = {
    'reservation_id': 'booking_id', 'reservation_date': 'booking_date',
    'date_of_booking': 'booking_date', 'booking_status': 'status',
    'selling_price': 'booking_value', 'total_amount': 'booking_value',
    'booking_amount': 'booking_value', 'booking_channel': 'channel',
    'hotel_name': 'property', 'property_name': 'property',
    'hotel_city': 'city', 'room_category': 'room_type', 'hotel_rating': 'star_rating',
    'stars': 'star_rating', 'purchase_cost': 'cost', 'supplier_cost': 'cost',
}
STATUSES = {'confirmed': 'Confirmed', 'booked': 'Confirmed',
            'cancelled': 'Cancelled', 'canceled': 'Cancelled',
            'completed': 'Completed', 'checked_out': 'Completed',
            'pending': 'Pending', 'no_show': 'No-show', 'noshow': 'No-show'}


class DataError(ValueError):
    """A user-correctable input problem."""


@dataclass
class QualityResult:
    accepted: pd.DataFrame
    rejected: pd.DataFrame
    issues: pd.DataFrame
    summary: dict


def read_upload(content: bytes, filename: str) -> pd.DataFrame:
    if len(content) > 20 * 1024 * 1024:
        raise DataError('Please use a file smaller than 20 MB.')
    suffix = filename.lower().rsplit('.', 1)[-1]
    if suffix not in {'csv', 'xlsx'}:
        raise DataError('Use a UTF-8 CSV or an .xlsx Excel workbook.')
    try:
        if suffix == 'csv':
            reader = csv.reader(StringIO(content.decode('utf-8-sig'), newline=''), strict=True)
            headers = next(reader, [])
            rows = []
            for row in reader:
                # A blank record still occupies a source row and must be audited.
                row = row or [''] * len(headers)
                if len(row) != len(headers):
                    raise DataError('CSV records must have the same number of fields as the header.')
                rows.append(row)
                if len(rows) > 100_000:
                    raise DataError('Version 1 supports up to 100,000 rows per dataset.')
            frame = pd.DataFrame(rows, columns=headers)
        else:
            sheet = pd.read_excel(BytesIO(content), dtype=str, engine='openpyxl',
                                  header=None, keep_default_na=False)
            headers = sheet.iloc[0].tolist() if not sheet.empty else []
            frame = sheet.iloc[1:].copy() if not sheet.empty else pd.DataFrame()
            frame.columns = headers
            frame = frame.reset_index(drop=True)
        names = [ALIASES.get(normalize_name(c), normalize_name(c)) for c in headers]
        if len(names) != len(set(names)):
            raise DataError('Duplicate headers map to the same field. Rename or remove the ambiguous column.')
    except DataError:
        raise
    except Exception as exc:
        raise DataError('Could not read this file. Check its format, encoding and first-sheet headers.') from exc
    if frame.empty:
        raise DataError('This file has no booking rows.')
    if len(frame) > 100_000:
        raise DataError('Version 1 supports up to 100,000 rows per dataset.')
    return frame


def normalize_name(value):
    return re.sub(r'[^a-z0-9]+', '_', str(value).strip().lower()).strip('_')


def validate(frame: pd.DataFrame) -> QualityResult:
    raw = frame.copy().reset_index(drop=True)
    names = [ALIASES.get(normalize_name(c), normalize_name(c)) for c in raw.columns]
    if len(set(names)) != len(names):
        raise DataError('Two columns map to the same field. Rename or remove the ambiguous column.')
    raw.columns = names
    missing = sorted(set(REQUIRED) - set(names))
    if missing:
        raise DataError('Missing required columns: ' + ', '.join(missing))
    data = raw[[c for c in REQUIRED + OPTIONAL if c in raw]].copy()
    issues = []
    bad = pd.Series(False, index=data.index)

    def record(mask, column, reason, action, reject=False):
        for index in data.index[mask]:
            issues.append({'source_row': int(index) + 2, 'column': column,
                           'issue': reason, 'action': action})
        if reject:
            bad.loc[mask] = True

    for col in sorted(set(names) - set(REQUIRED + OPTIONAL)):
        issues.append({'source_row': None, 'column': col, 'issue': 'Unrecognized column',
                       'action': 'Not stored or exported; keep your original file'})
    data['booking_id'] = data['booking_id'].astype('string').str.strip().replace('', pd.NA)
    record(data.booking_id.isna(), 'booking_id', 'Missing identifier', 'Quarantined', True)
    # Restrict strings to ISO dates to avoid silently guessing day/month order.
    date_text = data.booking_date.astype('string').str.strip()
    dates = pd.to_datetime(date_text.where(date_text.str.match(r'^\d{4}-\d{2}-\d{2}(?:[ T].*)?$').fillna(False)),
                           errors='coerce', format='ISO8601', utc=True)
    data['booking_date'] = dates.dt.tz_convert(None).dt.normalize()
    record(data.booking_date.isna(), 'booking_date', 'Missing or invalid ISO date', 'Quarantined', True)
    data['status'] = data.status.astype('string').map(lambda x: STATUSES.get(normalize_name(x)))
    record(data.status.isna(), 'status', 'Missing or unsupported status', 'Quarantined', True)
    for col in ['booking_value', 'cost', 'star_rating']:
        if col not in data:
            data[col] = np.nan
            continue
        original = data[col]
        converted = pd.to_numeric(original, errors='coerce').astype(float)
        invalid = ~np.isfinite(converted) | (converted < 0)
        if col == 'star_rating':
            invalid |= (converted < 1) | (converted > 5) | (converted % 1 != 0)
        absent = original.isna() | original.astype('string').str.strip().eq('').fillna(False)
        if col == 'booking_value':
            record(invalid, col, 'Missing, negative or invalid monetary value', 'Quarantined', True)
        else:
            record(invalid & ~absent, col, 'Invalid optional numeric value', 'Set to missing; row retained')
            record(absent, col, 'Missing optional value', 'Retained as missing')
        data[col] = converted.mask(invalid)
    for col in DIMENSIONS:
        if col not in data:
            data[col] = 'Unknown'
        else:
            clean = data[col].astype('string').str.strip().replace('', pd.NA)
            record(clean.isna(), col, 'Missing dimension', 'Filled with Unknown')
            data[col] = clean.fillna('Unknown')
    # Identical canonical records keep the first; conflicting IDs quarantine all versions.
    exact = data.duplicated(keep='first')
    record(exact, 'booking_id', 'Duplicate canonical record', 'Excluded duplicate; first retained', True)
    unique = data.loc[~exact]
    conflict_ids = unique.loc[unique.booking_id.duplicated(keep=False), 'booking_id'].dropna()
    conflict = data.booking_id.isin(conflict_ids)
    record(conflict, 'booking_id', 'Conflicting records for identifier', 'All versions quarantined', True)
    data['source_row'] = data.index + 2
    accepted = data.loc[~bad].reset_index(drop=True)
    rejected = data.loc[bad].copy()
    # Rejected values remain available in original source; persisted audit is PII-minimized.
    report = pd.DataFrame(issues, columns=['source_row', 'column', 'issue', 'action'])
    return QualityResult(accepted, rejected, report, {
        'input_rows': len(raw), 'accepted_rows': len(accepted),
        'quarantined_rows': int(bad.sum()), 'duplicate_rows': int(exact.sum()),
        'conflicting_rows': int(conflict.sum()), 'issue_count': len(report),
        'ignored_columns': sorted(set(names) - set(REQUIRED + OPTIONAL)),
        'missing_optional_columns': sorted(set(OPTIONAL) - set(names)),
    })
