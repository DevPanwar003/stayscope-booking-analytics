"""Descriptive cancellation comparisons on accepted, currently filtered bookings.

Rates always use all rows. Invalid monetary values never become zero-valued
cancellations: affected totals are unavailable, and value bands expose those rows.
"""
from math import sqrt
from numbers import Integral

import numpy as np
import pandas as pd

from src.validation import DataError, STATUSES


def wilson_interval(cancelled, bookings):
    """95% Wilson score interval; (None, None) for an empty denominator."""
    if (not isinstance(cancelled, Integral) or not isinstance(bookings, Integral)
            or cancelled < 0 or bookings < 0 or cancelled > bookings):
        raise ValueError('Counts must be integers with 0 <= cancelled <= bookings.')
    if bookings == 0:
        return None, None
    # NumPy integer exponentiation can overflow before conversion to float.
    cancelled, bookings = int(cancelled), int(bookings)
    z = 1.959963984540054
    p = cancelled / bookings
    denominator = 1 + z * z / bookings
    center = (p + z * z / (2 * bookings)) / denominator
    margin = z * sqrt(p * (1 - p) / bookings + z * z / (4 * bookings ** 2)) / denominator
    return (0.0 if cancelled == 0 else max(0.0, center - margin),
            1.0 if cancelled == bookings else min(1.0, center + margin))


def _prepare(data, dimension):
    missing = sorted({'status', 'booking_value', dimension} - set(data.columns))
    if missing:
        raise DataError('Missing required columns: ' + ', '.join(missing))
    if not data.status.isin(set(STATUSES.values())).all():
        raise DataError('Cancellation analysis requires validated, non-missing booking statuses.')
    work = data.copy().reset_index(drop=True)
    values = pd.to_numeric(work.booking_value, errors='coerce').astype(float)
    work['booking_value'] = values.where(np.isfinite(values) & values.ge(0))
    return work


def cancellation_benchmark(data, dimension, minimum=20):
    """Every observed segment, its filtered benchmark, value completeness and CI.

    minimum flags small groups; it never removes rows or changes the benchmark.
    Missing categories are explicitly grouped as Unknown. Input is not mutated.
    """
    if not isinstance(minimum, Integral) or minimum < 1:
        raise ValueError('Minimum bookings must be a positive integer.')
    work = _prepare(data, dimension)
    work[dimension] = work[dimension].astype('string').str.strip().replace('', pd.NA).fillna('Unknown')
    work['_cancelled'] = work.status.eq('Cancelled').astype(int)
    work['_cancelled_value'] = work.booking_value.where(work._cancelled.eq(1), 0.0)
    work['_invalid_cancelled_value'] = work._cancelled.eq(1) & work.booking_value.isna()
    groups = work.groupby(dimension, observed=True, sort=False).agg(
        bookings=('status', 'size'), cancelled=('_cancelled', 'sum'),
        booking_value=('booking_value', 'sum'),
        cancelled_booking_value=('_cancelled_value', 'sum'),
        invalid_cancelled_values=('_invalid_cancelled_value', 'sum'),
        valid_values=('booking_value', 'count')).reset_index()
    groups['booking_value'] = groups.booking_value.where(groups.valid_values.eq(groups.bookings))
    groups['cancelled_booking_value'] = groups.cancelled_booking_value.where(groups.invalid_cancelled_values.eq(0))
    groups['cancellation_rate'] = groups.cancelled / groups.bookings
    groups['overall_cancellation_rate'] = work._cancelled.mean() if len(work) else np.nan
    groups['difference_pp'] = 100 * (groups.cancellation_rate - groups.overall_cancellation_rate)
    intervals = [wilson_interval(int(k), int(n)) for k, n in zip(groups.cancelled, groups.bookings)]
    groups['ci_lower'] = [lo for lo, _ in intervals]
    groups['ci_upper'] = [hi for _, hi in intervals]
    groups['small_sample'] = groups.bookings.lt(minimum)
    groups['sample_note'] = np.where(groups.small_sample, 'Small sample — interpret cautiously', 'Meets selected threshold')
    return groups.drop(columns='valid_values').sort_values('bookings', ascending=False, kind='stable').reset_index(drop=True)


def booking_value_segments(data, minimum=20, bands=4):
    """Quantiles recomputed within selection; ties stay together, empty bins omitted.

    Invalid values get an explicit band so counts still reconcile to input rows.
    Canonical app data contains no invalid monetary values after validation.
    """
    if not isinstance(bands, Integral) or not 1 <= bands <= 10:
        raise ValueError('Number of bands must be an integer between 1 and 10.')
    work = _prepare(data, 'booking_value')
    work['value_band'] = 'Unavailable value'
    valid = work.booking_value.dropna()
    order = []
    if not valid.empty:
        if valid.nunique() == 1:
            label = f'B1 · {valid.iloc[0]:,.6g} (all equal)'
            work.loc[valid.index, 'value_band'] = label
            order = [label]
        else:
            codes, edges = pd.qcut(valid, q=min(bands, len(valid)), labels=False, retbins=True, duplicates='drop')
            labels = {i: f'B{i + 1} · {edges[i]:,.6g}–{edges[i + 1]:,.6g}' for i in sorted(codes.unique())}
            work.loc[valid.index, 'value_band'] = codes.map(labels)
            order = list(labels.values())
    result = cancellation_benchmark(work, 'value_band', minimum)
    order.append('Unavailable value')
    return result.sort_values('value_band', key=lambda s: s.map({label: i for i, label in enumerate(order)})).reset_index(drop=True)


def cancellation_insights(groups, dimension, currency, minimum=20):
    """Bounded observations with denominators and investigative next steps."""
    if not isinstance(minimum, Integral) or minimum < 1:
        raise ValueError('Minimum bookings must be a positive integer.')
    if groups.empty:
        return ['No bookings match this selection. Broaden filters before comparing segments.']
    total = int(groups.bookings.sum())
    overall = float(groups.overall_cancellation_rate.iloc[0])
    eligible = groups[groups.bookings.ge(minimum)]
    messages = []
    above = eligible[eligible.difference_pp > 0].sort_values('difference_pp', ascending=False).head(2)
    for row in above.to_dict('records'):
        messages.append(f"Observed: {row[dimension]} has {row['cancellation_rate']:.1%} cancellations "
                        f"({row['cancelled']}/{row['bookings']}), {row['difference_pp']:+.1f} percentage points "
                        f"versus {overall:.1%} overall (n={total}). This may help prioritize retention review. "
                        'Investigate booking terms and customer mix; these are hypotheses, not proven causes.')
    if len(eligible) >= 2:
        ordered = eligible.sort_values('cancellation_rate')
        low, high = ordered.iloc[0], ordered.iloc[-1]
        messages.append(f'Observed comparison: {high[dimension]} {high.cancellation_rate:.1%} '
                        f'({int(high.cancelled)}/{int(high.bookings)}) versus {low[dimension]} '
                        f'{low.cancellation_rate:.1%} ({int(low.cancelled)}/{int(low.bookings)}). '
                        'Use this to scope a like-for-like review of dates and booking conditions before testing changes.')
    valued = groups[groups.cancelled_booking_value.notna()]
    if not valued.empty and valued.cancelled_booking_value.max() > 0:
        top = valued.sort_values('cancelled_booking_value', ascending=False).iloc[0]
        complete = groups.invalid_cancelled_values.sum() == 0
        amount = float(groups.cancelled_booking_value.sum())
        share = f'{top.cancelled_booking_value / amount:.1%} of selected cancelled booking value' if complete else 'share unavailable because other values are missing'
        messages.append(f'Observed: {top[dimension]} has {currency} {top.cancelled_booking_value:,.2f} '
                        f'associated with cancellations ({int(top.cancelled)}/{int(top.bookings)} bookings; {share}). '
                        'Review these bookings and payment/refund records to understand financial exposure; this is not lost revenue or profit.')
    invalid = int(groups.invalid_cancelled_values.sum())
    if invalid:
        messages.append(f'Incomplete monetary evidence: {invalid}/{int(groups.cancelled.sum())} cancelled bookings '
                        f'have unavailable values (selection n={total}). Affected segment totals and overall value shares '
                        'are unavailable. Check the original amounts before prioritizing financial exposure.')
    small = int(groups.bookings.lt(minimum).sum())
    if small:
        messages.append(f'Limited evidence: {small}/{len(groups)} segments have fewer than {minimum} bookings '
                        f'(selection n={total}). Collect more comparable observations before acting on rate differences.')
    if not messages:
        messages.append(f'Observed: no above-benchmark segment meets the {minimum}-booking threshold '
                        f'(overall {overall:.1%}, n={total}). Review a broader comparable period before proposing changes.')
    return messages
