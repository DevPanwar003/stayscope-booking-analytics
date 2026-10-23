"""Reports share dashboard calculations and neutralize spreadsheet formulas."""
from io import BytesIO
import json
import re
import pandas as pd
from src.analytics import FORMULAS, insights, kpis


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


def excel_bytes(data, context=None):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        spreadsheet_safe(summary_frame(data, context), excel=True).to_excel(writer, sheet_name='Summary', index=False)
        spreadsheet_safe(data, excel=True).to_excel(writer, sheet_name='Filtered bookings', index=False)
    return output.getvalue()
