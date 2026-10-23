"""Shared metrics: booking value is neither recognized revenue nor cash."""
import pandas as pd

FORMULAS = {
    'Total bookings': 'Count of accepted filtered rows.',
    'Confirmed bookings': 'Count with status Confirmed (Completed is separate).',
    'Cancelled bookings': 'Count with status Cancelled.',
    'Cancellation rate': 'Cancelled bookings / all filtered bookings; undefined when empty.',
    'Total booking value': 'Sum of booking_value across all statuses, including cancellations.',
    'Retained booking value': 'Sum of booking_value for Confirmed and Completed only; not revenue or cash.',
    'Average booking value': 'Total booking value / total bookings; undefined when empty.',
    'Retained markup': 'Sum of booking_value minus cost for Confirmed/Completed; unavailable if any eligible cost is missing. Not accounting profit.',
}


def filter_bookings(data, start=None, end=None, selections=None):
    mask = pd.Series(True, index=data.index)
    if start is not None:
        mask &= data.booking_date >= pd.Timestamp(start)
    if end is not None:
        mask &= data.booking_date < pd.Timestamp(end) + pd.Timedelta(days=1)
    for column, values in (selections or {}).items():
        if values is not None:  # [] intentionally means zero matches.
            mask &= data[column].isin(values)
    return data.loc[mask].copy()


def kpis(data):
    total = len(data)
    cancelled = int(data.status.eq('Cancelled').sum())
    retained = data.loc[data.status.isin(['Confirmed', 'Completed'])]
    cost_available = 'cost' in retained and retained.cost.notna().all() and len(retained) > 0
    return {
        'Total bookings': total,
        'Confirmed bookings': int(data.status.eq('Confirmed').sum()),
        'Cancelled bookings': cancelled,
        'Cancellation rate': cancelled / total if total else None,
        'Total booking value': float(data.booking_value.sum()),
        'Retained booking value': float(retained.booking_value.sum()),
        'Average booking value': float(data.booking_value.mean()) if total else None,
        'Retained markup': float((retained.booking_value - retained.cost).sum()) if cost_available else None,
    }


def breakdown(data, dimension):
    work = data.assign(cancelled=data.status.eq('Cancelled').astype(int))
    result = work.groupby(dimension, dropna=False).agg(
        bookings=('booking_id', 'size'), cancelled=('cancelled', 'sum'),
        booking_value=('booking_value', 'sum')).reset_index()
    result['cancellation_rate'] = result.cancelled / result.bookings
    return result.sort_values('bookings', ascending=False)


def monthly(data):
    work = data.assign(period=data.booking_date.dt.to_period('M').astype(str))
    return breakdown(work, 'period').sort_values('period')


def insights(data, minimum=20):
    if len(data) < minimum:
        return [f'Insufficient sample: {len(data)} bookings. At least {minimum} are required for comparative observations.']
    messages = []
    overall = kpis(data)['Cancellation rate']
    for row in breakdown(data, 'channel').itertuples():
        if row.bookings >= minimum and row.cancellation_rate >= overall + .05:
            messages.append(f'{row.channel}: cancellation rate {row.cancellation_rate:.1%} '
                            f'({row.cancelled}/{row.bookings}), versus {overall:.1%} overall '
                            f'(n={len(data)}). Difference is descriptive, not causal.')
    rooms = breakdown(data, 'room_type')
    total_value = float(data.booking_value.sum())
    if total_value > 0:
        leaders = rooms[rooms.booking_value == rooms.booking_value.max()]
        for top in leaders.itertuples():
            ranking = 'ties for' if len(leaders) > 1 else 'contributes'
            messages.append(f'{top.room_type} {ranking} the largest booking-value share: '
                            f'{top.booking_value / total_value:.1%} (n={int(top.bookings)}).')
    if not messages:
        messages.append('No rule thresholds were met for this selection. No trend is inferred.')
    return messages
