"""Exercise the new controls against real UI, charts and filtered exports."""
from datetime import date
from pathlib import Path
import shutil

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.validation import read_upload, validate


@pytest.fixture
def app(tmp_path):
    root = Path(__file__).resolve().parents[1]
    shutil.copy(root / 'app.py', tmp_path / 'app.py')
    (tmp_path / 'data').mkdir()
    shutil.copy(root / 'data/sample_hotel_bookings.csv', tmp_path / 'data')
    return AppTest.from_file(str(tmp_path / 'app.py'), default_timeout=30).run()


@pytest.mark.parametrize('dimension', ['channel', 'room_type', 'city', 'property', 'star_rating', 'booking_period'])
def test_all_dimensions_and_threshold_preserve_totals(app, dimension):
    app.radio[0].set_value('Cancellation explorer').run()
    next(item for item in app.selectbox if item.label == 'Compare by').set_value(dimension).run()
    assert not app.exception and not app.error
    groups = app.dataframe[0].value
    assert dimension in groups and groups.bookings.sum() == 1800 and groups.cancelled.sum() == 325
    assert (groups.overall_cancellation_rate == 325 / 1800).all()
    assert app.dataframe[1].value.bookings.sum() == 1800
    before = groups.drop(columns=['small_sample', 'sample_note'])
    app.slider[0].set_value(100).run()
    pd.testing.assert_frame_equal(before, app.dataframe[0].value.drop(columns=['small_sample', 'sample_note']))
    assert (app.dataframe[0].value.small_sample == (groups.bookings < 100)).all()


@pytest.mark.parametrize('dimension', ['city', 'property', 'channel', 'room_type', 'status', 'rating', 'dates'])
def test_filtered_advanced_charts_tables_and_exports(app, tmp_path, monkeypatch, dimension):
    import src.charts as charts
    import src.exports as exports
    full = validate(read_upload((tmp_path / 'data/sample_hotel_bookings.csv').read_bytes(), 'sample.csv')).accepted
    if dimension == 'dates':
        app.date_input[0].set_value((date(2025, 2, 1), date(2025, 2, 28)))
        expected = full[full.booking_date.between('2025-02-01', '2025-02-28')]
    elif dimension == 'rating':
        app.multiselect(key='rating_1').set_value(['5 stars'])
        expected = full[full.star_rating == 5]
    else:
        selected = sorted(full[dimension].unique())[0]
        app.multiselect(key=f'{dimension}_1').set_value([selected])
        expected = full[full[dimension] == selected]
    captured, exported = [], []
    original_chart, original_excel = charts.chart, exports.excel_bytes

    def capture(data, *args, **kwargs):
        captured.append(data.copy())
        return original_chart(data, *args, **kwargs)

    def export(data, context=None):
        exported.append(data.copy())
        return original_excel(data, context)

    monkeypatch.setattr(charts, 'chart', capture)
    monkeypatch.setattr(exports, 'excel_bytes', export)
    app.radio[0].set_value('Cancellation explorer').run()
    assert not app.exception and not app.error
    assert len(captured) == 3
    for groups in [*captured, app.dataframe[0].value, app.dataframe[1].value]:
        assert groups.bookings.sum() == len(expected)
        assert groups.cancelled.sum() == expected.status.eq('Cancelled').sum()
        assert groups.cancelled_booking_value.sum() == pytest.approx(expected.loc[expected.status.eq('Cancelled'), 'booking_value'].sum())
        assert (groups.overall_cancellation_rate == expected.status.eq('Cancelled').mean()).all()
    assert sorted(exported[-1].booking_id) == sorted(expected.booking_id)
    assert any('CURRENT VIEW' in item.value for item in app.caption)


def test_empty_selection_and_import_notice(app):
    app.multiselect(key='channel_1').set_value([])
    app.radio[0].set_value('Cancellation explorer').run()
    assert not app.exception
    assert any('No bookings match' in item.value for item in app.info)
    assert not app.dataframe
    app.radio[0].set_value('Import & quality').run()
    assert any('SYNTHETIC DEMONSTRATION DATA' in item.value for item in app.info)


def test_excel_uses_selected_comparison_threshold(app, monkeypatch):
    from io import BytesIO
    import src.exports as exports
    original = exports.excel_bytes
    captured = []

    def capture(data, context=None):
        result = original(data, context)
        captured.append((dict(context), result))
        return result

    monkeypatch.setattr(exports, 'excel_bytes', capture)
    app.radio[0].set_value('Cancellation explorer').run()
    next(item for item in app.selectbox if item.label == 'Compare by').set_value('city')
    app.slider[0].set_value(100).run()
    assert not app.exception
    context, payload = captured[-1]
    assert context['comparison_dimension'] == 'city'
    assert context['minimum_group_size'] == 100
    table = pd.read_excel(BytesIO(payload), sheet_name='Cancellation benchmarks')
    assert table.minimum_group_size.eq(100).all()
    assert table.small_sample.equals(table.bookings.lt(100))
