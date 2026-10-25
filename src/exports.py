"""Reports share dashboard calculations and neutralize spreadsheet formulas."""
from io import BytesIO
import json
import re
import pandas as pd
from src.analytics import FORMULAS, insights, kpis
from src.advanced_analytics import cancellation_benchmark, booking_value_segments


def spreadsheet_safe(frame, excel=False):
    result = frame.copy()
    for column in result.select_dtypes(include=['object', 'string']).columns:
        if excel:
            # Show forbidden XML control bytes explicitly instead of dropping them.
            result[column] = result[column].map(lambda v: re.sub(
                r'[\x00-\x08\x0b\x0c\x0e-\x1f]', lambda match: f'\\x{ord(match.group()):02x}', v)
                if isinstance(v, str) else v)
        result[column] = result[column].map(
            lambda v: "'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v)
    return result


def csv_bytes(frame):
    return spreadsheet_safe(frame).to_csv(index=False).encode('utf-8-sig')


def summary_frame(data, context=None):
    rows = [{'section': 'KPI', 'name': key, 'value': value, 'definition': FORMULAS[key]}
            for key, value in kpis(data).items()]
    rows += [{'section': 'Finding', 'name': str(i + 1), 'value': item, 'definition': 'Rule-based observation'}
             for i, item in enumerate(insights(data))]
    rows += [{'section': 'Context', 'name': key, 'value': json.dumps(value, default=str), 'definition': ''}
             for key, value in (context or {}).items()]
    return pd.DataFrame(rows)


def advanced_report_tables(data, context=None):
    """All six comparisons share the dashboard denominator and selected threshold."""
    context = context or {}
    minimum = context.get('minimum_group_size', 20)
    currency = context.get('currency', 'Unspecified units')
    work = data.copy()
    for name in ['channel', 'room_type', 'city', 'property']:
        if name not in work:
            work[name] = 'Unknown'
    if 'star_rating' not in work:
        work['star_rating'] = float('nan')
    work['star_rating'] = work.star_rating.map(lambda value: 'Unknown' if pd.isna(value) else f'{int(value)} stars')
    dates = pd.to_datetime(work.get('booking_date', pd.Series(pd.NaT, index=work.index)), errors='coerce')
    work['booking_period'] = dates.dt.to_period('M').astype('string').fillna('Unknown')
    frames = []
    for dimension in ['channel', 'room_type', 'city', 'property', 'star_rating', 'booking_period']:
        frame = cancellation_benchmark(work, dimension, minimum).rename(columns={dimension: 'segment'})
        frame.insert(0, 'dimension', dimension)
        frames.append(frame)
    benchmarks = pd.concat(frames, ignore_index=True)
    bands = booking_value_segments(work, minimum)
    for frame in [benchmarks, bands]:
        frame['currency'] = currency
        frame['minimum_group_size'] = minimum
    definitions = {
        'Scope': 'All currently filtered rows. Each dimension repeats the same population; never sum bookings across dimensions.',
        'Currency': currency,
        'Minimum group size': str(minimum),
        'Selected comparison': context.get('comparison_dimension', 'All dimensions; default threshold'),
        'Provenance': 'Synthetic demonstration; not real hotel results' if context.get('synthetic') else 'Uploaded or unspecified dataset; provenance is not independently verified',
        'Empty selection': 'Zero rows produces header-only analytical tables; no cancellation rate is inferred.',
        'bookings': 'All filtered rows in the segment, including Confirmed, Completed, Cancelled, Pending and No-show.',
        'cancelled': 'Rows with status exactly Cancelled.',
        'cancellation_rate': 'cancelled / bookings. Stored as a fraction and displayed as a percentage in Excel.',
        'overall_cancellation_rate': 'Cancelled / all filtered bookings. Includes the compared segment.',
        'difference_pp': '100 × (segment cancellation rate − overall cancellation rate); percentage points, not percent change.',
        'booking_value': 'Selling value across all statuses; not recognized revenue or cash.',
        'cancelled_booking_value': 'Selling value attached to cancelled records; not automatically lost revenue, cash or profit.',
        'Unavailable values': 'Unavailable marks an undefined or incomplete total. Invalid cancelled amounts are counted in invalid_cancelled_values, not treated as zero.',
        'ci_lower / ci_upper': 'Descriptive 95% Wilson bounds for an independent-binomial proportion. No correction for clustering, selection bias or multiple comparisons.',
        'small_sample / sample_note': 'Threshold is a caution only; small groups remain included. It is not a significance test.',
        'Value bands': 'Up to four quantile bands within this selection. Ties stay together; empty bins are omitted. First lower boundary included, otherwise right-closed; displayed edges rounded.',
        'Causality': 'Interval overlap or separation alone is not a test of differences or evidence of causation. Investigate hypotheses with additional data.',
        'Missing categories': 'Unknown includes unavailable optional fields; no categories or ratings are inferred.',
    }
    guide = pd.DataFrame(definitions.items(), columns=['Metric or topic', 'Definition or caveat'])
    return {'Cancellation benchmarks': benchmarks, 'Value bands': bands, 'Report guide': guide}


def excel_bytes(data, context=None):
    additional = advanced_report_tables(data, context)
    # Legacy summary observations need these optional categories, but the original
    # booking sheet must retain exactly the caller's columns and records.
    summary_data = data.copy()
    for name in ['channel', 'room_type']:
        if name not in summary_data:
            summary_data[name] = 'Unknown'
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        spreadsheet_safe(summary_frame(summary_data, context), excel=True).to_excel(writer, sheet_name='Summary', index=False)
        spreadsheet_safe(data, excel=True).to_excel(writer, sheet_name='Filtered bookings', index=False)
        for name, frame in additional.items():
            spreadsheet_safe(frame, excel=True).to_excel(writer, sheet_name=name, index=False, na_rep='Unavailable')
            sheet = writer.sheets[name]
            sheet.freeze_panes = 'A2'
            sheet.auto_filter.ref = sheet.dimensions
            for column in sheet.columns:
                header = column[0].value
                sheet.column_dimensions[column[0].column_letter].width = 70 if name == 'Report guide' else 24
                for cell in column[1:]:
                    if header in {'cancellation_rate', 'overall_cancellation_rate', 'ci_lower', 'ci_upper'}:
                        cell.number_format = '0.0%'
                    elif header in {'booking_value', 'cancelled_booking_value'}:
                        cell.number_format = '#,##0.00'
                    elif header == 'difference_pp':
                        cell.number_format = '+0.00;-0.00;0.00'
    return output.getvalue()
