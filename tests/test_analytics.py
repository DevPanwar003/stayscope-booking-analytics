import pandas as pd
import pytest
from src.analytics import breakdown, filter_bookings, insights, kpis, monthly


def test_exact_kpis(clean):
    assert kpis(clean) == {
        'Total bookings': 4, 'Confirmed bookings': 1, 'Cancelled bookings': 1,
        'Cancellation rate': .25, 'Total booking value': 1000.,
        'Retained booking value': 400., 'Average booking value': 250., 'Retained markup': 130.,
    }


def test_empty_kpis(clean):
    result = kpis(clean.iloc[:0])
    assert result['Total bookings'] == 0
    assert result['Cancellation rate'] is None
    assert result['Average booking value'] is None
    assert result['Retained markup'] is None


def test_incomplete_cost_is_not_zero_profit(clean):
    clean.loc[0, 'cost'] = None
    assert kpis(clean)['Retained markup'] is None
    assert kpis(clean.drop(columns='cost'))['Retained markup'] is None


def test_missing_cancelled_cost_does_not_affect_retained_markup(clean):
    clean.loc[1, 'cost'] = None
    assert kpis(clean)['Retained markup'] == 130


def test_inclusive_date_filter(clean):
    result = filter_bookings(clean, '2025-01-01', '2025-01-31')
    assert result.booking_id.tolist() == ['A', 'B']


@pytest.mark.parametrize('selections,expected', [
    ({'channel': ['Direct']}, ['A', 'C']),
    ({'room_type': ['Suite']}, ['B', 'C']),
    ({'channel': ['Direct'], 'room_type': ['Suite']}, ['C']),
    ({'channel': []}, []), ({'city': ['Goa'], 'status': ['Confirmed']}, ['A']),
    ({'star_rating': [5]}, ['C']),
])
def test_filters(clean, selections, expected):
    assert filter_bookings(clean, selections=selections).booking_id.tolist() == expected


def test_rates_include_denominators(clean):
    groups = breakdown(clean, 'channel').set_index('channel')
    assert groups.loc['OTA', 'bookings'] == 2
    assert groups.loc['OTA', 'cancellation_rate'] == .5
    assert groups.loc['Direct', 'cancellation_rate'] == 0
    assert monthly(clean).booking_value.tolist() == [300, 700]


def test_insights_are_data_driven(clean):
    assert 'Insufficient sample' in insights(clean)[0]
    observations = insights(pd.concat([clean] * 20, ignore_index=True))
    assert any('50.0%' in text and '40' in text for text in observations)
    assert any('50.0%' in text and 'Suite' in text for text in observations)


def test_every_status_reconciles_and_enters_rate_denominator(clean):
    # Include all five supported states, including the states without KPI cards.
    data = pd.concat([clean, clean.iloc[[0]]], ignore_index=True)
    data.loc[4, 'booking_id'] = 'E'
    data.loc[4, 'status'] = 'No-show'
    groups = breakdown(data, 'status').set_index('status')
    result = kpis(data)
    assert set(groups.index) == {'Confirmed', 'Completed', 'Cancelled', 'Pending', 'No-show'}
    assert groups.bookings.sum() == result['Total bookings'] == 5
    assert result['Confirmed bookings'] + result['Cancelled bookings'] + groups.loc[
        ['Completed', 'Pending', 'No-show'], 'bookings'].sum() == result['Total bookings']
    assert result['Cancellation rate'] == 1 / 5
    selected = filter_bookings(data, selections={'status': ['Cancelled', 'Pending', 'No-show']})
    assert kpis(selected)['Cancellation rate'] == 1 / 3
