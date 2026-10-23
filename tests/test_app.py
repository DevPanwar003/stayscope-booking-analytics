from pathlib import Path
import shutil
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app(tmp_path):
    root = Path(__file__).resolve().parents[1]
    shutil.copy(root / 'app.py', tmp_path / 'app.py')
    (tmp_path / 'data').mkdir()
    shutil.copy(root / 'data' / 'sample_hotel_bookings.csv', tmp_path / 'data')
    return AppTest.from_file(str(tmp_path / 'app.py'), default_timeout=30).run()


def test_overview_and_filter_empty_state(app):
    assert not app.exception
    assert app.metric[0].value == '1,800'
    app.multiselect(key='channel_1').set_value([]).run()
    assert not app.exception
    assert app.metric[0].value == '0'
    assert any('No bookings match' in element.value for element in app.info)


@pytest.mark.parametrize('page', ['Cancellation explorer', 'Dataset explorer', 'Import & quality'])
def test_pages(app, page):
    app.radio[0].set_value(page).run()
    assert not app.exception
    assert not app.error


def test_status_and_date_filters(app):
    app.multiselect(key='status_1').set_value(['Cancelled']).run()
    assert not app.exception
    assert app.metric[3].value == '100.0%'
    app.radio[0].set_value('Cancellation explorer').run()
    assert any('one booking status' in message.value for message in app.warning)


def test_upload_review_save_and_duplicate(app, raw):
    app.radio[0].set_value('Import & quality').run()
    app.file_uploader[0].set_value(('test.csv', raw.to_csv(index=False).encode(), 'text/csv')).run()
    assert not app.exception
    save = next(button for button in app.button if button.label == 'Save reviewed dataset')
    assert save.disabled
    app.checkbox[0].check().run()
    next(button for button in app.button if button.label == 'Save reviewed dataset').click().run()
    assert not app.exception
    assert any('saved' in item.value for item in app.success)
    next(button for button in app.button if button.label == 'Save reviewed dataset').click().run()
    assert any('Already imported' in item.value for item in app.success)
    app.radio[0].set_value('Overview').run()
    app.selectbox[0].set_value(2).run()
    assert app.metric[0].value == '4'
    assert not app.exception


def test_malformed_upload_is_friendly(app):
    app.radio[0].set_value('Import & quality').run()
    app.file_uploader[0].set_value(('bad.csv', b'wrong,headers\na,b', 'text/csv')).run()
    assert not app.exception
    assert 'Missing required columns' in app.error[0].value


@pytest.mark.parametrize('change', ['file', 'currency'])
def test_review_confirmation_is_bound_to_upload_and_currency(app, raw, change):
    app.radio[0].set_value('Import & quality').run()
    app.file_uploader[0].set_value(('first.csv', raw.to_csv(index=False).encode(), 'text/csv')).run()
    app.checkbox[0].check().run()
    if change == 'file':
        raw.loc[0, 'booking_value'] = 999
        app.file_uploader[0].set_value(('second.csv', raw.to_csv(index=False).encode(), 'text/csv')).run()
    else:
        next(item for item in app.selectbox if item.label.startswith('Dataset currency')).set_value('USD').run()
    assert not app.exception
    assert not app.checkbox[0].value
    assert next(button for button in app.button if button.label == 'Save reviewed dataset').disabled


def test_saved_dataset_appears_immediately(app, raw):
    app.radio[0].set_value('Import & quality').run()
    app.file_uploader[0].set_value(('new.csv', raw.to_csv(index=False).encode(), 'text/csv')).run()
    app.checkbox[0].check().run()
    next(button for button in app.button if button.label == 'Save reviewed dataset').click().run()
    assert any('new.csv' in option for option in next(item for item in app.selectbox if item.label == 'Active dataset').options)


def test_failed_demo_restore_preserves_database(app, tmp_path):
    import sqlite3
    sample = tmp_path / 'data' / 'sample_hotel_bookings.csv'
    sample.write_text('invalid,headers\na,b\n', encoding='utf-8')
    app.radio[0].set_value('Import & quality').run()
    app.text_input[0].set_value('RESET DEMO').run()
    next(button for button in app.button if button.label == 'Reset synthetic demo').click().run()
    with sqlite3.connect(tmp_path / 'data' / 'bookings.db') as db:
        assert db.execute('SELECT COUNT(*) FROM bookings').fetchone()[0] == 1800
    assert not app.exception
    assert app.error


@pytest.mark.parametrize('dimension', ['city', 'property', 'channel', 'room_type', 'status', 'rating', 'dates', 'combined'])
def test_filters_reach_every_chart_table_and_export(app, tmp_path, monkeypatch, dimension):
    """Exercise real widgets; observe actual chart/export inputs, not a mock app."""
    from datetime import date
    from io import BytesIO
    import pandas as pd
    import src.charts as charts
    import src.exports as exports
    from src.analytics import kpis
    from src.validation import validate, read_upload

    sample = tmp_path / 'data' / 'sample_hotel_bookings.csv'
    full = validate(read_upload(sample.read_bytes(), sample.name)).accepted
    expected = full.copy()
    observed_charts, observed_csv, observed_excel = [], [], []
    original_chart, original_csv, original_excel = charts.chart, exports.csv_bytes, exports.excel_bytes

    def capture_chart(data, x, y, title, **kwargs):
        observed_charts.append((data.copy(), x, y))
        return original_chart(data, x, y, title, **kwargs)

    def capture_csv(data):
        output = original_csv(data)
        observed_csv.append((data.copy(), output))
        return output

    def capture_excel(data, context=None):
        output = original_excel(data, context)
        observed_excel.append((data.copy(), context, output))
        return output

    monkeypatch.setattr(charts, 'chart', capture_chart)
    monkeypatch.setattr(exports, 'csv_bytes', capture_csv)
    monkeypatch.setattr(exports, 'excel_bytes', capture_excel)
    if dimension in ['city', 'property', 'channel', 'room_type', 'status']:
        selected = sorted(full[dimension].unique())[0]
        app.multiselect(key=f'{dimension}_1').set_value([selected])
        expected = expected[expected[dimension] == selected]
    elif dimension == 'rating':
        app.multiselect(key='rating_1').set_value(['5 stars'])
        expected = expected[expected.star_rating == 5]
    elif dimension == 'dates':
        app.date_input[0].set_value((date(2025, 2, 1), date(2025, 2, 28)))
        expected = expected[expected.booking_date.between('2025-02-01', '2025-02-28')]
    else:
        app.multiselect(key='city_1').set_value(['Goa'])
        app.multiselect(key='channel_1').set_value(['Direct'])
        expected = expected[(expected.city == 'Goa') & (expected.channel == 'Direct')]
    app.run()
    assert not app.exception
    assert len(expected) > 0
    metrics = kpis(expected)
    for card, (label, value) in zip(app.metric, metrics.items()):
        display = 'N/A' if value is None else f'{value:.1%}' if label == 'Cancellation rate' else (
            f'{value:,.0f}' if 'bookings' in label else f'{value:,.2f}')
        assert card.value == display

    assert len(observed_charts) == (8 if metrics['Retained markup'] is not None else 7)
    for frame, x, y in observed_charts:
        source = expected.copy()
        if x == 'period':
            source[x] = source.booking_date.dt.to_period('M').astype(str)
        if x == 'star_rating':
            source[x] = source[x].map(lambda value: f'{int(value)} stars')
        if y == 'markup':
            source = source[source.status.isin(['Confirmed', 'Completed'])]
            source['markup'] = source.booking_value - source.cost
            values = source.groupby(x).markup.sum()
        elif y == 'bookings':
            values = source.groupby(x).size()
        elif y == 'cancellation_rate':
            values = source.assign(cancelled=source.status == 'Cancelled').groupby(x).cancelled.mean()
            assert frame.bookings.sum() == len(expected)
        else:
            values = source.groupby(x).booking_value.sum()
        pd.testing.assert_series_equal(frame.set_index(x)[y].sort_index(), values.sort_index(),
                                       check_names=False, check_dtype=False, check_index_type=False)
    property_table = app.dataframe[0].value
    assert property_table.bookings.sum() == len(expected)
    assert property_table.booking_value.sum() == pytest.approx(expected.booking_value.sum())

    def assert_exports():
        record_csv = next(payload for frame, payload in observed_csv if 'booking_id' in frame)
        assert sorted(pd.read_csv(BytesIO(record_csv)).booking_id) == sorted(expected.booking_id)
        summary = next(frame for frame, _ in observed_csv if 'section' in frame)
        assert summary.query('name == "Total booking value"').value.iloc[0] == pytest.approx(expected.booking_value.sum())
        frame, context, workbook_bytes = observed_excel[-1]
        assert sorted(frame.booking_id) == sorted(expected.booking_id)
        assert context['dataset_id'] == 1
        workbook = pd.read_excel(BytesIO(workbook_bytes), sheet_name=None)
        assert sorted(workbook['Filtered bookings'].booking_id) == sorted(expected.booking_id)

    assert_exports()
    observed_csv.clear()
    app.radio[0].set_value('Cancellation explorer').run()
    assert not app.exception
    assert app.dataframe[0].value.bookings.sum() == len(expected)
    assert_exports()
    observed_csv.clear()
    app.radio[0].set_value('Dataset explorer').run()
    assert not app.exception
    assert sorted(app.dataframe[0].value.booking_id) == sorted(expected.booking_id)
    assert_exports()


@pytest.mark.parametrize('case', ['empty', 'missing', 'invalid_date', 'missing_value', 'duplicate', 'minimal'])
def test_upload_quality_edge_cases(app, raw, case):
    import pandas as pd
    app.radio[0].set_value('Import & quality').run()
    if case == 'empty':
        raw = raw.iloc[:0]
    elif case == 'missing':
        raw = raw.drop(columns='booking_date')
    elif case == 'invalid_date':
        raw.loc[0, 'booking_date'] = 'not a date'
    elif case == 'missing_value':
        raw.loc[0, 'booking_value'] = None
    elif case == 'duplicate':
        raw = pd.concat([raw, raw.iloc[[0]]], ignore_index=True)
    else:
        raw = raw[['booking_id', 'booking_date', 'status', 'booking_value']]
    app.file_uploader[0].set_value(('case.csv', raw.to_csv(index=False).encode(), 'text/csv')).run()
    assert not app.exception
    if case in ['empty', 'missing']:
        assert app.error
        assert not any(button.label == 'Save reviewed dataset' for button in app.button)
    else:
        expected_accepted = 3 if case in ['invalid_date', 'missing_value'] else 4
        assert app.metric[1].value == str(expected_accepted)
        if case == 'minimal':
            app.checkbox[0].check().run()
            next(button for button in app.button if button.label == 'Save reviewed dataset').click().run()
            app.radio[0].set_value('Overview').run()
            app.selectbox[0].set_value(2).run()
            assert app.metric[-1].value == 'N/A'
            assert not app.exception


@pytest.mark.parametrize('dimension', ['room_type', 'city', 'booking_period'])
def test_cancellation_dimension_controls(app, dimension):
    app.radio[0].set_value('Cancellation explorer').run()
    next(item for item in app.selectbox if item.label == 'Compare by').set_value(dimension).run()
    assert not app.exception
    table = app.dataframe[0].value
    assert dimension in table
    assert table.bookings.sum() == 1800
    assert table.cancelled.sum() == 325


def test_saved_upload_survives_fresh_application_processes(app, tmp_path, raw):
    """Execute the complete app in two fresh Python processes against one test DB."""
    import hashlib
    import json
    import subprocess
    import sys
    app.radio[0].set_value('Import & quality').run()
    app.file_uploader[0].set_value(('persisted.csv', raw.to_csv(index=False).encode(), 'text/csv')).run()
    app.checkbox[0].check().run()
    next(button for button in app.button if button.label == 'Save reviewed dataset').click().run()
    database = tmp_path / 'data' / 'bookings.db'
    before = hashlib.sha256(database.read_bytes()).hexdigest()
    code = '''
import json, sys
from streamlit.testing.v1 import AppTest
app = AppTest.from_file(sys.argv[1], default_timeout=30).run()
assert not app.exception, str(app.exception)
assert not app.error, str(app.error)
assert app.selectbox[0].value == 2
assert app.metric[0].value == '4'
assert app.metric[4].value == '1,000.00'
assert any('persisted.csv' in option for option in app.selectbox[0].options)
print(json.dumps({'bookings': app.metric[0].value, 'dataset': app.selectbox[0].value}))
'''
    for _ in range(2):
        process = subprocess.run([sys.executable, '-c', code, str(tmp_path / 'app.py')],
                                 cwd=Path(__file__).resolve().parents[1], capture_output=True,
                                 text=True, timeout=45)
        assert process.returncode == 0, process.stderr
        assert json.loads(process.stdout.strip().splitlines()[-1]) == {'bookings': '4', 'dataset': 2}
        assert hashlib.sha256(database.read_bytes()).hexdigest() == before


@pytest.mark.parametrize('page', ['Overview', 'Cancellation explorer', 'Dataset explorer'])
def test_synthetic_notice_remains_on_analytical_pages(app, page):
    app.radio[0].set_value(page).run()
    assert not app.exception
    assert any('SYNTHETIC DEMONSTRATION DATA' in item.value and 'Not real hotel results' in item.value
               for item in app.info)
