"""Manually verifiable cancellation examples; no live database access."""
import numpy as np
import pandas as pd
import pytest

from src.advanced_analytics import (
    booking_value_segments, cancellation_benchmark, cancellation_insights, wilson_interval,
)
from src.analytics import filter_bookings, kpis
from src.charts import chart
from src.validation import DataError


def test_benchmark_counts_rates_value_and_threshold(clean):
    original = clean.copy(deep=True)
    result = cancellation_benchmark(clean, 'channel', minimum=3).set_index('channel')
    assert result.bookings.to_dict() == {'Direct': 2, 'OTA': 2}
    assert result.cancelled.to_dict() == {'Direct': 0, 'OTA': 1}
    assert result.cancellation_rate.to_dict() == {'Direct': 0, 'OTA': .5}
    assert result.overall_cancellation_rate.tolist() == [.25, .25]
    assert result.difference_pp.to_dict() == {'Direct': -25, 'OTA': 25}
    assert result.cancelled_booking_value.to_dict() == {'Direct': 0, 'OTA': 200}
    assert result.small_sample.all()
    assert not cancellation_benchmark(clean, 'channel', minimum=2).small_sample.any()
    pd.testing.assert_frame_equal(clean, original)


@pytest.mark.parametrize('k,n,expected', [
    (0, 0, (None, None)), (0, 10, (0, .2775327998628892)),
    (10, 10, (.7224672001371107, 1)), (5, 10, (.236593090512564, .763406909487436)),
    (0, 1, (0, .7934506856227626)), (1, 1, (.20654931437723745, 1)),
])
def test_wilson_known_values(k, n, expected):
    actual = wilson_interval(k, n)
    if n == 0:
        assert actual == expected
    else:
        assert actual == pytest.approx(expected)
        assert 0 <= actual[0] <= k / n <= actual[1] <= 1


@pytest.mark.parametrize('k,n', [(-1, 10), (11, 10), (0, -1), (1.5, 3), (1, float('inf'))])
def test_wilson_rejects_impossible_counts(k, n):
    with pytest.raises(ValueError):
        wilson_interval(k, n)


@pytest.mark.parametrize('column', ['status', 'booking_value', 'channel'])
def test_missing_required_column(clean, column):
    with pytest.raises(DataError, match='Missing required columns'):
        cancellation_benchmark(clean.drop(columns=column), 'channel')


@pytest.mark.parametrize('status', [None, 'not a status'])
def test_invalid_status_cannot_silently_reduce_rate(clean, status):
    clean.loc[0, 'status'] = status
    with pytest.raises(DataError, match='validated'):
        cancellation_benchmark(clean, 'channel')


def test_empty_retains_output_schema(clean):
    groups = cancellation_benchmark(clean.iloc[:0], 'channel')
    assert groups.empty
    assert {'channel', 'bookings', 'ci_lower', 'difference_pp', 'cancelled_booking_value'} <= set(groups)
    assert booking_value_segments(clean.iloc[:0]).empty
    assert 'No bookings' in cancellation_insights(groups, 'channel', 'INR')[0]


def test_null_and_blank_categories_are_explicit(clean):
    clean.loc[[0, 1], 'channel'] = [None, ' ']
    row = cancellation_benchmark(clean, 'channel').set_index('channel').loc['Unknown']
    assert row.bookings == 2 and row.cancelled == 1 and row.cancellation_rate == .5


@pytest.mark.parametrize('bad', [None, 'bad', -1, np.inf, -np.inf])
def test_invalid_cancelled_money_is_unavailable_not_zero(clean, bad):
    clean['booking_value'] = clean.booking_value.astype(object)
    clean.loc[1, 'booking_value'] = bad
    groups = cancellation_benchmark(clean, 'channel').set_index('channel')
    assert pd.isna(groups.loc['OTA', 'cancelled_booking_value'])
    assert groups.loc['OTA', 'invalid_cancelled_values'] == 1
    assert groups.loc['OTA', 'cancellation_rate'] == .5
    bands = booking_value_segments(clean).set_index('value_band')
    assert bands.bookings.sum() == 4
    assert bands.loc['Unavailable value', 'cancelled'] == 1


def test_missing_non_cancelled_value_does_not_hide_valid_cancelled_total(clean):
    clean.loc[3, 'booking_value'] = np.nan
    row = cancellation_benchmark(clean, 'channel').set_index('channel').loc['OTA']
    assert row.cancelled_booking_value == 200
    assert pd.isna(row.booking_value)


@pytest.mark.parametrize('values', [[100]*4, [100, 100, 100, 200], [100, 100, 200, 200], [None]*4, [100, 200, 300, 400]])
def test_bands_reconcile_ties_and_missing_values(clean, values):
    clean['booking_value'] = values
    original = clean.copy(deep=True)
    bands = booking_value_segments(clean, minimum=2)
    assert bands.bookings.sum() == 4
    assert bands.cancelled.sum() == 1
    assert (bands.overall_cancellation_rate == .25).all()
    assert len(bands) <= 4
    assert (bands.bookings > 0).all()
    pd.testing.assert_frame_equal(clean, original)


def test_value_bands_known_sorted_results(clean):
    result = booking_value_segments(clean, minimum=1)
    assert result.bookings.tolist() == [1, 1, 1, 1]
    assert result.cancellation_rate.tolist() == [0, 1, 0, 0]
    assert result.cancelled_booking_value.tolist() == [0, 200, 0, 0]
    assert booking_value_segments(clean.iloc[[1]]).cancellation_rate.tolist() == [1]


def test_duplicate_dataframe_index_does_not_duplicate_rows(clean):
    clean.index = [0]*4
    assert booking_value_segments(clean).bookings.sum() == 4


def test_unused_categorical_levels_do_not_create_empty_groups(clean):
    clean['channel'] = pd.Categorical(clean.channel, categories=['Direct', 'OTA', 'unused'])
    assert len(cancellation_benchmark(clean, 'channel')) == 2


def test_filters_and_existing_kpis_keep_their_definitions(clean):
    selected = filter_bookings(clean, selections={'status': ['Cancelled', 'Pending']})
    result = cancellation_benchmark(selected, 'channel')
    assert result.overall_cancellation_rate.iloc[0] == kpis(selected)['Cancellation rate'] == .5
    assert result.cancelled_booking_value.sum() == 200
    assert kpis(clean)['Total booking value'] == 1000
    assert kpis(clean)['Retained booking value'] == 400


def test_insights_include_evidence_caution_and_action(clean):
    groups = cancellation_benchmark(clean, 'channel', 2)
    text = ' '.join(cancellation_insights(groups, 'channel', 'USD', 2))
    assert '1/2' in text and 'n=4' in text and '+25.0' in text
    assert 'USD 200.00' in text and 'Investigate' in text and 'not proven causes' in text
    assert 'Limited evidence' in ' '.join(cancellation_insights(cancellation_benchmark(clean, 'channel'), 'channel', 'INR'))


def test_chart_uses_actual_intervals_and_benchmark(clean):
    groups = cancellation_benchmark(clean, 'channel')
    figure = chart(groups, 'channel', 'cancellation_rate', 'Test', percent=True, confidence=True, benchmark=.25)
    assert list(figure.data[0].y) == [0, .5]
    assert list(figure.data[0].error_y.array) == pytest.approx((groups.ci_upper - groups.cancellation_rate).tolist())
    assert list(figure.data[0].error_y.arrayminus) == pytest.approx((groups.cancellation_rate - groups.ci_lower).tolist())
    assert figure.layout.shapes[0].y0 == .25


def test_end_date_includes_entire_day_without_numpy_deprecation(clean):
    import warnings
    clean.loc[1, 'booking_date'] = pd.Timestamp('2025-01-31 23:59:59.999999999')
    with warnings.catch_warnings():
        warnings.simplefilter('error', DeprecationWarning)
        result = filter_bookings(clean, '2025-01-01', '2025-01-31')
    assert result.booking_id.tolist() == ['A', 'B']


def test_wilson_numpy_integer_counts_do_not_overflow():
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('error', RuntimeWarning)
        actual = wilson_interval(np.int64(2_000_000_000), np.int64(4_000_000_000))
    assert actual == pytest.approx(wilson_interval(2_000_000_000, 4_000_000_000))
    assert actual[0] < .5 < actual[1]


def test_insight_threshold_matches_its_stated_minimum(clean):
    groups = cancellation_benchmark(clean, 'channel', minimum=2)
    original = groups.copy(deep=True)
    messages = cancellation_insights(groups, 'channel', 'INR', minimum=20)
    assert any('2/2 segments have fewer than 20' in message for message in messages)
    assert not any('percentage points' in message or 'Observed comparison' in message for message in messages)
    pd.testing.assert_frame_equal(groups, original)


def test_all_invalid_cancelled_values_produce_an_explicit_warning(clean):
    clean.loc[1, 'booking_value'] = np.nan
    text = ' '.join(cancellation_insights(cancellation_benchmark(clean, 'channel'), 'channel', 'INR'))
    assert '1/1 cancelled bookings' in text and 'Check the original amounts' in text
    assert 'nan' not in text.lower().split()


@pytest.mark.parametrize('minimum', [0, -1, 1.5])
def test_benchmark_and_insights_reject_invalid_thresholds(clean, minimum):
    with pytest.raises(ValueError, match='positive integer'):
        cancellation_benchmark(clean, 'channel', minimum)
    with pytest.raises(ValueError, match='positive integer'):
        cancellation_insights(cancellation_benchmark(clean, 'channel'), 'channel', 'INR', minimum)


@pytest.mark.parametrize('bands', [0, 11, 2.5])
def test_value_segments_reject_invalid_band_counts(clean, bands):
    with pytest.raises(ValueError, match='between 1 and 10'):
        booking_value_segments(clean, bands=bands)


def test_chart_hover_formats_rates_without_mutating_inputs(clean):
    groups = cancellation_benchmark(clean, 'channel')
    original = groups.copy(deep=True)
    hover = {'bookings': True}
    figure = chart(groups, 'channel', 'cancellation_rate', 'Rates', percent=True, hover=hover)
    assert '%{y:.1%}' in figure.data[0].hovertemplate
    assert hover == {'bookings': True}
    pd.testing.assert_frame_equal(groups, original)
    money = chart(groups, 'channel', 'cancelled_booking_value', 'INR')
    assert '%{y:,.2f}' in money.data[0].hovertemplate
