# StayScope Booking Intelligence — Python / BI portfolio project

## Résumé bullets

- Built a local hotel-booking analytics application with Python, pandas, Streamlit and Plotly, combining four dashboard pages with shared filters and SQLite snapshot persistence.
- Implemented auditable data validation, duplicate/conflict handling, cancellation benchmarks with Wilson intervals, and CSV/five-sheet Excel reporting with documented KPI definitions.
- Verified analytics, imports, persistence and UI behavior with 164 passing automated tests; used a clearly labelled 1,800-booking synthetic dataset to develop reproducible business questions and recommendations.

The test count refers to the recorded local suite; remote CI is pending. No production users, deployment, financial savings or performance improvements are claimed.

## Interview introduction

“I built StayScope to demonstrate how I turn booking files into trustworthy analysis. I focused on explicit validation decisions, consistent filter scope and interpretable cancellation comparisons. The application stores separate SQLite snapshots and exports the same selected records used by the dashboard. My case study uses synthetic data, so I present the findings as hypotheses to investigate rather than real hotel outcomes.”

## Likely technical questions

1. **Why use all bookings as the cancellation denominator?** All selected canonical statuses represent bookings in the population. Cancelled / (Confirmed + Cancelled) would omit Completed, Pending and No-show. A status filter deliberately changes that population and is disclosed in the UI.
2. **How are bad data and duplicates handled?** Required-field errors quarantine rows; exact canonical duplicates keep one; conflicting IDs quarantine every version. Optional costs remain missing, and retained markup is withheld if any eligible cost is absent. Raw source files are not overwritten.
3. **What do Wilson intervals establish?** They describe uncertainty around a binomial proportion under independence assumptions. They do not correct for clustering or multiple comparisons, and overlap/separation does not prove causality or substitute for a comparison test.
4. **Why SQLite and how are imports protected?** It supports local persistent snapshots without a server dependency. Values use parameterized SQL; transactions protect writes. Reset requires explicit confirmation and targets the demo. The app has no authentication or encrypted database and is not production hardened.
5. **How do you prove dashboards and exports agree?** Shared analytics functions consume the filtered accepted records. Tests inspect KPIs, chart/table inputs and actual workbook/CSV payloads, including empty/missing values and formula-like text. Streamlit AppTest exercises navigation and uploads using disposable databases. Remote CI and broader browser coverage remain separate verification work.

[Case study](PORTFOLIO_CASE_STUDY.md) · [Verification record](../TEST_RESULTS.md) · [README](../README.md)
