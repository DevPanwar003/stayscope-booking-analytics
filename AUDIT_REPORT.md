# StayScope quality audit — 23 October 2026

**Reliability follow-up:** the existing 90-test suite was rerun successfully, then expanded to **95 passed, 0 failed, 0 skipped** (67.35 seconds). Added coverage confirms status reconciliation, synthetic notices and persisted uploads across fresh application processes. No new genuine failures or application changes were required. See [TEST_RESULTS.md](TEST_RESULTS.md) for the latest commands and evidence; the detailed audit below records the earlier 90-test run.

## Scope and preservation

Audited the existing application in place. Preserved its four pages, sidebar navigation, styling, charts, filters and working import/export functionality. No deployment, live reset, live upload, data deletion or Git publication was performed. All destructive/reset and malformed-upload tests used disposable temporary databases and sample files.

Inventory:

| Item | Location |
|---|---|
| Streamlit entry point | `app.py` |
| Validation, cleaning and aliases | `src/validation.py` |
| SQLite persistence and resets | `src/database.py` |
| KPIs, filters, group comparisons and insights | `src/analytics.py` |
| CSV/XLSX generation | `src/exports.py` |
| Plotly presentation | `src/charts.py` |
| Synthetic generator | `src/sample.py` |
| Live local DB | `data/bookings.db` |
| Seeded sample | `data/sample_hotel_bookings.csv` |
| Setup scripts | `scripts/init_db.py`, `scripts/generate_sample.py` |
| New read-only reconciliation | `scripts/audit_metrics.py` |
| Tests | `tests/test_analytics.py`, `test_validation.py`, `test_database_exports.py`, `test_app.py`, `test_audit_regressions.py` |

The project directory has no `.git` repository. No existing source files were replaced wholesale, and the sample data was preserved.

## Test results

| Run | Passed | Failed | Notes |
|---|---:|---:|---|
| Existing suite before changes | 52 | 0 | 13.53 seconds |
| First new parsing/audit/export regression run | 2 | 5 | Reproduced five real defects before fixes |
| Focused filter integration run after test corrections | 8 | 0 | 19.87 seconds; 20 unrelated tests deselected |
| Final complete suite | **90** | **0** | **54.66 seconds**, no skips |

The audit added 38 test cases. Import confirmation, stale dataset selection, failed demo restoration and changed quarantine evidence were also reproduced with failing tests before their fixes. During integration-test development, assertions were corrected for SQLite's unspecified row order, equivalent string/object index types, and the intentionally absent markup chart for cancelled-only selections. Those assertion assumptions were not application defects.

Final command from the project directory:

```powershell
..\..\work\.venv\Scripts\python.exe -m pytest -q --tb=short
```

## Independently reconciled actual data

The live database contains one synthetic INR snapshot with 1,800 rows. All 1,800 canonical business records match the sample CSV. The read-only audit calculated metrics directly from SQLite rows using Python `Decimal`, independently of Pandas aggregation, and compared them with the app's KPI function. All eight matched within 0.000001. SQLite integrity check returned `ok`; foreign-key violations: 0.

| KPI | Verified value | Formula and assumptions |
|---|---:|---|
| Total bookings | 1,800 | Count accepted rows in the selected snapshot/filter |
| Confirmed bookings | 372 | Status exactly Confirmed, excluding Completed |
| Cancelled bookings | 325 | Status exactly Cancelled |
| Cancellation rate | 18.0555556% | 325 / 1,800; display rounds to 18.1%; all statuses enter denominator |
| Total booking value | INR 30,780,317.38 | Sum selling value across all statuses, including Cancelled/Pending/No-show |
| Retained booking value | INR 23,328,909.64 | Sum selling value for Confirmed + Completed; 1,370 rows |
| Average booking value | INR 17,100.176322… | 30,780,317.38 / 1,800; display rounds to 17,100.18 |
| Retained markup | INR 5,226,332.11 | Sum(value − supplier cost) across the 1,370 retained rows; all 1,370 have costs |

These are booking measures, not earned revenue or collected cash. Markup excludes commissions, taxes and overheads and is not accounting profit. Zero-row averages/rates are undefined, shown as N/A. Markup is N/A if there are no retained bookings or any eligible cost is missing; missing cancelled-booking costs do not affect it. Negative markup is valid. Dates filter booking date inclusively; timestamp inputs normalize to UTC day. Each dataset must have a single confirmed currency; conversion is not performed.

## Defects fixed

| Defect | Before | Fix and evidence |
|---|---|---|
| Ambiguous upload headers | Pandas renamed exact duplicate headers, allowing an arbitrary monetary column to be analyzed | Check original CSV/XLSX headers before constructing the analysis frame; reject duplicate canonical names. Tests cover both formats and unequal CSV field counts. |
| Literal `NA` identifiers lost | Default NA inference quarantined valid text IDs | Preserve strings during CSV/XLSX reading; tests retain `NA`. Empty identifiers remain invalid. |
| Blank CSV records skipped | Rows disappeared and later source references shifted | Preserve and quarantine blank logical records; regression checks count and source row. |
| Quarantine ID corruption | JSON loading converted `001` to numeric `1` | Disable inferred dtype conversion in audit JSON reads; persisted round-trip tested. |
| Excel export crash | A control byte in a text field raised `IllegalCharacterError` during ordinary dashboard rendering | Escape XML-incompatible controls visibly in XLSX output; workbook round-trip tested. CSV and database source text remain unchanged. |
| Stale import approval | Review checkbox stayed checked after changing file or currency | Bind review state to content + currency; both transitions require fresh review. |
| Stale active-dataset choices | Newly saved dataset was absent from the selector until another interaction | Rerun after import with a one-time success message; immediate availability tested. |
| Non-atomic demo reset | Malformed replacement sample could delete the existing demo and then crash | Validate first; perform deletion and replacement in one transaction. Invalid-sample and insertion-failure tests prove original demo/uploaded data survives. |
| Audit snapshot collision | Different rejected bookings with identical quality totals reused the first import's audit | Compare detailed audit evidence and assign a distinct fingerprint on collision, preserving compatibility with existing fingerprints. Repeated equivalent imports remain idempotent. |
| Misleading status guidance | Cancellation page told users to clear a filter, which yields zero rows | Guidance now says select all statuses. |
| Hardcoded provenance count | Demo banner always claimed 1,800 generated rows and a fixed generator provenance | Banner derives the accepted snapshot count from loaded data. The bundled sample's seed remains documented separately. |

Duplicate lookup and insert now share a serialized transaction. A two-thread equivalent-import test verifies one snapshot is created. SQL values remain parameterized; a hostile-looking identifier is stored literally without affecting tables. Failed imports roll back both metadata and partially inserted bookings.

## Filters, navigation and exports

Widget-level integration tests individually select city, property, channel, room type, status, star rating and date range, plus a city/channel combination. They verify all overview KPI values and every applicable chart's actual input data against independently grouped selected rows. They then navigate to Cancellation explorer and Dataset explorer and verify counts/records remain filtered. The property summary is also reconciled.

Each tested view's actual generated CSV and XLSX bytes are read back to verify booking IDs and summaries; context records dataset, currency and filters. Cancellation dimension controls (channel, room type, city and month) are exercised. Zero-match filters, empty export schemas, malformed/empty CSV files, missing required columns, missing values, duplicates, invalid dates, absent optional fields, timezone dates, missing costs, negative markup and formula-like spreadsheet text have automated coverage.

Intentional exceptions:

- The original import-quality report is dataset-wide and explicitly labeled; it must not change with analytical filters.
- Plotly zoom/legend changes and table sorting/searching are presentation actions, not changes to the sidebar filter state.
- Comparison dimension and sample-size threshold affect the cancellation view, not the KPI report. The report exports shared filtered records, KPIs and rule-based findings, not every page-specific chart.
- Visiting Import can reset analytical widget selections because those widgets are no longer rendered; saved filter views are outside V1.

No placeholder business buttons or fabricated live KPIs were found. Streamlit's framework toolbar is not a custom deployment feature. The live app reloaded the updated provenance text, retained its visual layout, returned `ok` from the health endpoint, and had no captured browser console errors. Automated navigation checks cover all four pages; this is not cross-browser certification.

## Dependencies and Windows instructions

Verified installed environment: Python 3.12.14, Pandas 2.3.3, NumPy 2.3.5, Streamlit 1.66.1, Plotly 6.9.0, openpyxl 3.1.5 and Pytest 9.1.1. `pip check` reports no broken requirements. `pip install --dry-run --no-index -r requirements.txt` succeeds with installed dependencies. Compilation checks passed.

README now distinguishes the existing bundled-runtime environment from a fresh portable `.venv`, includes `pip check`, explains the occupied-port case, and documents filter semantics, source-row numbering, atomic reset, screenshot guidance and limitations. A fresh-machine install and a Python-version matrix were not executed; no such success is claimed.

## Remaining limitations and priorities

No failing tests or unresolved ordinary-path crash was observed after the fixes. Remaining limitations include eager Excel generation on each rerun, no load/performance certification at the row limit, no authentication, session-local filters, absent financial-ledger fields, float-based money calculations, and Excel's 32,767-character cell limit (use CSV for long text). Original raw uploads/invalid values are not persisted. The full browser download/save dialog and a fresh-machine dependency installation were not separately automated; export contents and installed dependency consistency were verified.

Highest-value next steps for a recruiter-ready portfolio:

1. Initialize/version the project in Git and add a Windows/Linux Python test matrix with a CI badge. Verify a clean install in CI before claiming portability.
2. Capture real synthetic-data screenshots and a short demo recording following the README guidance, including an error/quality-review flow.
3. Write one concise hotel-manager case study: question, selected cohort, denominator, observation, limitation, and suggested follow-up. Link each reported number to an exported report and avoid causal claims.

The live DB SHA-256 before the audit was `672760AC61EDF01101B8AEBBCF9F226D4135502FFF1DB66B30A026257EB7C495`. Final preservation verification is recorded in `TEST_RESULTS.md`.
