# StayScope: investigating cancellation patterns

## Business problem and objectives

A booking portfolio can look healthy by total selling value while containing substantial cancellations or unreliable records. This project demonstrates how an analyst can reconcile status totals, compare segments with transparent denominators, and identify questions worth investigating. It is a synthetic exercise, not a hotel engagement or evidence of business impact.

## Dataset and cleaning

The bundled sample contains 1,800 fictional bookings across six Indian cities during 2025, generated with NumPy seed 42. Currency is INR. One record is one booking. No guest identities, payments, refunds, stay dates or room inventory are available.

The validator checks identifiers, ISO dates, canonical statuses and finite nonnegative booking values. Invalid required fields are quarantined; missing optional costs are not imputed. Exact duplicates retain one canonical row, while conflicting IDs quarantine all versions. Unknown columns are excluded. The bundled sample has 1,800 accepted rows and no row-level validation issues. See [the data guide](DATA_GUIDE.md).

## Approach and methods

Start with all dates and statuses. Reconcile KPIs and inspect distributions before filtering by city, property, channel, room type or rating. Examine monthly booking-date trends; these are not stay-date trends. Then compare cancellation rates by segment and booking-value quantile bands.

Cancellation rate is Cancelled / all selected rows, including Pending and No-show. Segment benchmarks include the segment itself. Differences are percentage points, not relative percentage changes. Descriptive 95% Wilson intervals accompany each rate. The minimum-size threshold (default 20) flags groups without removing them. It is not a significance test. Value bands are recalculated for the selection, keep ties together and can have unequal counts.

## Reproduced observations

Computed directly from the current validated sample using `kpis` and `cancellation_benchmark` on 24 October 2026; figures below are rounded for display.

- Status reconciliation: 372 Confirmed + 998 Completed + 325 Cancelled + 62 Pending + 43 No-show = **1,800**.
- Overall cancellation rate: **325 / 1,800 = 18.06%**.
- Total booking value: **INR 30,780,317.38**; retained value: **INR 23,328,909.64**.
- Average booking value: **INR 17,100.18**; retained markup: **INR 5,226,332.11**.

| Channel | Bookings | Cancelled | Rate | 95% Wilson interval | Cancelled booking value (INR) |
|---|---:|---:|---:|---|---:|
| Online travel agency | 808 | 222 | 27.48% | 24.51–30.65% | 3,995,276.82 |
| Direct | 536 | 57 | 10.63% | 8.30–13.53% | 906,711.11 |
| Corporate | 300 | 30 | 10.00% | 7.09–13.92% | 429,466.05 |
| Travel agent | 156 | 16 | 10.26% | 6.41–16.01% | 215,575.69 |

The synthetic online-travel-agency segment is 9.42 percentage points above the overall rate and contains the largest cancelled booking value. All four channels exceed the default 20-booking threshold. This is a generated pattern, not evidence that a channel causes cancellations or should receive less investment.

## Recommendations and follow-up investigations

For a real dataset, first verify comparable periods and booking terms. Compare the channel pattern within cities, properties and months to explore mix differences. Request lead time, cancellation timing and policy fields before proposing policy changes; these fields are absent here. Reconcile payment/refund records before translating cancelled booking value into financial exposure. Validate any intervention prospectively using an appropriate study design rather than treating descriptive differences as causal.

## Assumptions and limitations

Retained value includes Confirmed + Completed. Markup subtracts supplier costs only when all eligible costs exist; it excludes overhead and is not accounting profit. No occupancy, ADR, RevPAR or cash-flow claims can be made. Monetary storage uses floating point. Wilson intervals assume independent binomial observations and do not address clustering, selection bias or multiple comparisons. Quantile bands are relative to the current selection. Synthetic data cannot validate real-world recommendations or savings.

## Reproduce

From the project root with the environment activated:

```sh
python -m streamlit run app.py --server.address 127.0.0.1
python -m pytest -q -ra
```

Select the synthetic snapshot, all statuses and the full 2025 date range. Open Cancellation explorer, select Channel and threshold 20. Download Complete report · Excel. Compare the Summary and channel rows in Cancellation benchmarks; each dimension repeats the same population, so do not sum across dimensions.

For an independent reproducible table in Python:

```python
from pathlib import Path
from src.validation import read_upload, validate
from src.analytics import kpis
from src.advanced_analytics import cancellation_benchmark

raw = read_upload(Path("data/sample_hotel_bookings.csv").read_bytes(), "sample.csv")
result = validate(raw)
data = result.accepted
print(len(data))
print(kpis(data))
print(cancellation_benchmark(data, "channel", minimum=20).to_string(index=False))
```

[Return to README](../README.md)
