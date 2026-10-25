# Verification record

## Publication review — 25 October 2026

**164 passed, 0 failed, 0 skipped, 0 pytest warnings in 206.04 seconds.** JUnit confirms zero errors/failures/skips.

```powershell
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\publication-tests.xml
git diff --check
```

Reproduced every channel row in the case study (counts, rates, Wilson bounds and cancelled values), all reported monetary KPIs, and the 9.42 percentage-point comparison. Canonical sample records exactly matched the seeded generator. All four README screenshots are valid image files; documentation links resolve. Common credential-pattern checks of public candidates and reachable local history found no matches. The only public dataset/database/export candidate was the synthetic CSV. No tracked ignored files or candidate files above 1 MB were found. Remote-only history was not fetched; this is a limited scan, not a security guarantee.

**Publication cleanup pending:** the already tracked `t -qpython -m pytest -q` contains unrelated terminal pager help. It was preserved and not untracked. Omitting it from staging will not exclude it from a push. [PUBLICATION_REVIEW.md](docs/PUBLICATION_REVIEW.md) lists 22 intended files, their rationale and exact commands, including approval-dependent untracking that keeps the local copy. No history rewrite is proposed. README's stale case-study roadmap item and suggested repository name were corrected to reflect the existing project.

The diff check passed with only existing Git LF-to-CRLF notices. The database hash remained `AB188AABBE055088E5B9D7AE51C131141DFCDD9323274F87DBE0EDD0A5129231`. Application code/tests and datasets were unchanged in this review. Nothing was staged, committed, pushed, deployed or deleted. Remote CI and broader browser/platform checks remain pending.

## Portfolio documentation verification — 24 October 2026

**164 passed, 0 failed, 0 skipped, 0 pytest warnings in 317.18 seconds.** JUnit confirms zero failures, errors and skips. This run followed the README rewrite and creation of `docs/PORTFOLIO_CASE_STUDY.md` and `docs/RESUME_PROJECT_ENTRY.md`; application code, tests, dependencies, workflow and datasets were unchanged in this documentation pass.

```powershell
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\portfolio-docs-tests.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pip check
git diff --check
git ls-files -ci --exclude-standard
```

The suite includes all four Streamlit pages, import behavior and CSV/Excel regression checks. Dependency compatibility and whitespace checks passed; Git emitted only existing LF-to-CRLF notices. All local links in README and both new documents resolve, and all six existing PNGs passed image validation. The four README screenshots are each under 155 KB. The case-study reproduction code was executed against the bundled sample and its reported channel rates, intervals, sample sizes and values matched the output. Validation accepted all 1,800 sample records with zero issues.

Representative ignore checks confirmed local DBs, environments, private uploads, secrets and exports are excluded. No tracked ignored files or public candidate files above 1 MB were found. A limited scan for common private-key/GitHub/AWS credential patterns returned no matches; this is not an exhaustive secret audit. The database SHA256 remained `AB188AABBE055088E5B9D7AE51C131141DFCDD9323274F87DBE0EDD0A5129231`.

Windows commands use the same tested Python 3.12 environment; POSIX commands are documented but were not executed on another OS. Interactive browser checks were not repeated. Remote CI, broader platform/browser verification, load tests and a security assessment remain pending. No files were staged, committed, pushed, published or deleted.

## Final verification rerun — 24 October 2026

Full suite: **164 passed, 0 failed, 0 skipped, 0 pytest warnings in 289.84 seconds**. JUnit confirms 164 tests and zero errors/failures/skips (suite time 289.507 seconds). No warning suppression is configured in pytest.ini.

```powershell
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\final-pass-tests.xml
git diff --check
```

Current tracked diff and untracked analytics/tests/screenshots were reviewed and preserved. Existing database/export tests remain intact; their only tracked change is the expected five-sheet workbook contract. No new regression was found or application code changed during this verification.

A real workbook generated from the currently validated synthetic CSV was saved outside the repository at `../../work/final-verification/synthetic-report.xlsx` and read back. Expected sheets: Summary, Filtered bookings, Cancellation benchmarks, Value bands, Report guide. All Summary KPIs and all six benchmark dimensions agreed with the application's analytics, including rates, monetary totals, sample sizes, currency INR and threshold. The dataset has 1,800 bookings, 325 cancellations, cancellation rate 18.0555556%, total value INR 30,780,317.38, retained value INR 23,328,909.64, average value INR 17,100.1763222 and retained markup INR 5,226,332.11. These are synthetic demonstration values.

Additional workbook/CSV round-trip checks passed for empty selections, required-only columns, incomplete retained costs (markup unavailable), and category names containing Unicode, quotes, comma, newline and ampersand. Existing formula-neutralization tests passed. Booking and summary CSV row counts matched their sources. All four README screenshot paths resolved to valid images, verified by Pillow.

All four pages passed local Streamlit AppTest rendering/navigation in disposable databases, including Import & quality and its upload edge cases. This rerun did not repeat interactive browser inspection; earlier browser evidence remains recorded below. No new cross-browser/platform claims are made.

`git diff --check` passed with no whitespace defects. Git emitted LF-to-CRLF conversion notices for five Python files; these are Git notices, not pytest warnings or test failures. Live database SHA256 remained `AB188AABBE055088E5B9D7AE51C131141DFCDD9323274F87DBE0EDD0A5129231`. No live data was deleted or overwritten; no commit, push or deployment occurred. Remaining limits are remote CI execution, additional browser/platform testing, accessibility and load/security assessment.

## Latest portfolio-readiness verification — 24 October 2026

- Full suite: **164 passed, 0 failed, 0 skipped in 307.69 seconds**; no warnings reported. JUnit records zero errors, failures and skips (suite time 307.609 seconds).
- Focused exports/database/audit regressions: **30 passed, 0 failed, 0 skipped in 5.11 seconds**.
- Eight additional cases cover benchmark reconciliation, filters and thresholds, empty inputs, unavailable optional fields at small/large sample sizes, formula safety/formatting, unavailable monetary values and the UI-selected threshold reaching Excel.

Executed from this project directory in the existing isolated Windows Python 3.12.14 environment:

```powershell
..\..\work\stayscope-clean\Scripts\python.exe -m pytest tests/test_advanced_exports.py tests/test_database_exports.py tests/test_audit_regressions.py -q -ra --junitxml=..\..\work\portfolio-export-tests.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\portfolio-full-tests.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pip check
git diff --check
..\..\work\stayscope-clean\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8503 --server.headless true
```

Dependency compatibility passed. The existing code changes were inspected and preserved. No dependencies were added. The original Summary and Filtered bookings sheets remain, followed by Cancellation benchmarks, Value bands and Report guide. A real browser download (`booking_report.xlsx`) was opened with openpyxl: all five sheets were present, Filtered bookings contained 1,800 records, and each of six benchmark dimensions reconciled to 1,800 bookings / 325 cancellations. CSV export regressions also passed in the suite. Empty selections and missing optional fields are covered by automated workbook checks.

**Browser evidence:** a fresh loopback server on port 8503 rendered Overview, Cancellation explorer, Dataset explorer and Import & quality. Desktop inspection used 1440×1000; the Import & quality top section was additionally inspected at 480×850 and the viewport override was reset. No browser console errors were captured. The quality form showed the synthetic warning, upload rules, currency selector and disabled reset button without confirmation. No live upload/reset was performed. Genuine screenshots: `docs/screenshots/overview.png`, `cancellations-portfolio.png`, `dataset.png`, `quality.png`. The last depicts the empty intake form, not a validated upload. Only the synthetic snapshot was used for data screenshots.

**CI and limits:** the existing workflow installs dependencies, checks them, runs the suite and audits demo metrics on Windows/Ubuntu Python 3.12 for push, PR and manual dispatch. Read-only permissions and disabled persisted checkout credentials were reviewed. Remote execution of the new uncommitted code was not performed: no commit/push was authorized. Only the Codex in-app browser was available; separate Chrome, Edge, Firefox/Safari and other operating systems were not tested. Responsive spot checks are not full mobile-device or accessibility certification. Load tests and production security certification were not performed. Excel generation remains eager on reruns.

**Data preservation:** the live database SHA256 remained `AB188AABBE055088E5B9D7AE51C131141DFCDD9323274F87DBE0EDD0A5129231` during this task; the demo and existing uploaded snapshot were preserved. Nothing was deleted, staged, committed, pushed or deployed. Earlier records below describe prior runs and their then-current limitations.

## Previous Version 2.0 follow-up verification — 24 October 2026

After inspecting the existing Git diff and preserving all prior changes, the focused tests ran first, followed by the complete suite:

- Focused: **61 passed, 0 failed, 0 skipped in 56.97 seconds**.
- Complete: **156 passed, 0 failed, 0 skipped in 157.20 seconds**. No pytest warnings were reported in this run; the user-reported cache warning was not reproduced. JUnit confirms zero failures, errors and skips.

```powershell
..\..\work\stayscope-clean\Scripts\python.exe -m pytest tests/test_advanced_analytics.py tests/test_advanced_ui.py -q -ra --junitxml=..\..\work\v2-final-focused.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\v2-final-full.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pip check
..\..\work\stayscope-clean\Scripts\python.exe scripts/audit_metrics.py
git diff --check
```

Ten added regression cases cover NumPy integer overflow in Wilson calculations, insight threshold consistency, incomplete monetary evidence, invalid threshold/band parameters, and percentage/currency tooltip formatting without input mutation. All earlier tests remain intact, including CSV/Excel payload checks, navigation, filters, malformed imports and persistence.

Both comparison tables now share clear currency, rate, interval and count labels. The fresh local server on port 8502 rendered these labels successfully; no browser console errors were captured. A genuine synthetic-only table/insight screenshot is saved as `docs/screenshots/cancellation-details.png`. A disposable-copy startup/health check passed, as did dependency compatibility and whitespace validation.

**Data preservation:** during the continuation a second uploaded snapshot was observed alongside the original demo. Consequently the live database hash differs from the earlier one-snapshot baseline; this is not reported as an unchanged database across the entire session. Read-only verification found 1,800 demo rows and 1,685 uploaded rows, SQLite integrity `ok`, zero foreign-key violations, and matching KPI audits for both snapshots. Its SHA256 remained `AB188AABBE055088E5B9D7AE51C131141DFCDD9323274F87DBE0EDD0A5129231` across the final checks. No live import/reset/delete operation was performed by the agent.

No dependencies, existing tests, Git history or remote were replaced. Nothing was staged, committed, pushed or deployed. Remote CI, broader browser/platform testing and three remaining page screenshots are still pending. Advanced benchmark tables remain outside the original two-sheet Excel report, as documented in README.

## Version 2.0 verification — 24 October 2026

- Baseline: **95 passed, 0 failed, 0 skipped**, 75 warnings, 64.26 seconds.
- New focused analytics/UI suite: **51 passed, 0 failed, 0 skipped**, 33.47 seconds.
- Final full suite: **146 passed, 0 failed, 0 skipped**, 98.87 seconds; no warnings reported. JUnit confirms 146 tests, zero errors, failures or skips.
- Existing tests were preserved. The additional 51 cases cover manually calculated benchmark/value totals, Wilson boundaries, invalid/missing values and statuses, ties, empty inputs, duplicate indexes, all six comparison dimensions, threshold behavior and every sidebar filter reaching new chart/table inputs and Excel source rows.
- The date filter now uses a calendar-day offset; a regression test confirms the last nanosecond of the selected end date remains included without NumPy deprecation warnings.

Commands run from the project folder with the existing isolated Windows Python 3.12.14 environment:

```powershell
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\v2-baseline.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pytest tests/test_advanced_analytics.py tests/test_advanced_ui.py -q -ra --junitxml=..\..\work\v2-focused.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\v2-full.xml
..\..\work\stayscope-clean\Scripts\python.exe -m pip check
..\..\work\stayscope-clean\Scripts\python.exe scripts/audit_metrics.py
git diff --check
```

Dependency compatibility and diff whitespace checks passed. No configured linter was found. No dependencies were added or upgraded. The real Streamlit server also started successfully in a disposable copy; demo initialization, HTTP health, all eight independent KPI comparisons, SQLite integrity and foreign-key checks passed. Tests exercise imports/resets only in temporary databases.

The live database hash before and after remains `672760AC61EDF01101B8AEBBCF9F226D4135502FFF1DB66B30A026257EB7C495`. No data was deleted, Git history/remote changed, or commit/push/deployment performed.

**Browser/runtime evidence:** the old port-8501 process initially retained the previous chart function and raised an unexpected-keyword TypeError after hot reload. A fresh process using the same repository on loopback port 8502 loaded the new module correctly. Restart the old process with the same interpreter to clear its cached imports; do not reset the database. The fresh Cancellation explorer rendered the benchmark, Wilson error bars, currency-labelled cancelled values, value bands and insights without an exception. Desktop (1440×1000) and narrow (480×850) layouts were visually inspected, with no captured browser console errors. A genuine synthetic-demo capture is saved as `docs/screenshots/cancellations.png`.

This is local Windows verification, not remote CI, cross-browser certification, load testing or a security certification. New benchmark tables are not added to the established two-sheet Excel report. Synthetic patterns and descriptive intervals do not establish real-world business impact or causation.

## Previous portfolio documentation and clean-install verification — 24 October 2026

**95 passed, 0 failed, 0 skipped, 75 warnings in 195.68 seconds.** The full suite ran in a newly created Windows Python 3.12.14 virtual environment with `include-system-site-packages = false`. JUnit confirms the test counts. The baseline rerun before this work also passed all 95 tests (0 failures/errors/skips; JUnit duration 65.612 seconds).

Commands executed from the project folder (environment creation and installation originally ran from the surrounding workspace using equivalent paths):

```powershell
& 'C:\Users\devpa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv ..\..\work\stayscope-clean
..\..\work\stayscope-clean\Scripts\python.exe -m pip install -r requirements.txt
..\..\work\stayscope-clean\Scripts\python.exe -m pip check
..\..\work\stayscope-clean\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\clean-install-tests.xml
```

Installation succeeded and `pip check` reported no broken requirements. Resolved direct versions: pandas 2.3.3, NumPy 2.5.4, Streamlit 1.66.1, Plotly 6.9.0, openpyxl 3.1.5, pytest 9.1.1. `requirements-tested.txt` retains the earlier tested direct-version snapshot (NumPy 2.3.5); it is not the new environment's lockfile.

**Remaining warning:** 75 NumPy timedelta deprecation warnings originate at `src/analytics.py:21` during date filtering with this dependency combination. They do not fail current tests, but future dependency upgrades need verification. No warning suppression or weakened assertion was introduced.

A workspace-only smoke script (`work/verify_clean_setup.py`, outside the repository) copied the application and synthetic sample to a separate temporary directory. With the fresh interpreter, it ran `scripts/init_db.py`, `scripts/audit_metrics.py`, and a real Streamlit subprocess on a free loopback port. All eight KPIs reconciled; SQLite integrity was `ok`, foreign-key violations were zero, and HTTP `/_stcore/health` returned `ok`. Only that smoke subprocess was stopped. The existing dashboard and live database were preserved; the database SHA256 remains `672760AC61EDF01101B8AEBBCF9F226D4135502FFF1DB66B30A026257EB7C495`.

The new GitHub Actions Windows/Ubuntu workflow is configured but **has not run remotely**. This verifies a fresh virtual environment on this Windows machine, not a different machine, Linux compatibility, a load test or production security. Genuine screenshot capture remains pending. Application source, tests and dependencies were not changed in this documentation/CI task.

Git inspection found initial commit `63176f6`, branch `main`, and an existing `origin`. No Git configuration/history was changed and nothing was staged, committed or pushed. Tracked files contain the synthetic CSV but no ignored local database, environment, upload or secret file. Common credential-pattern scanning found no matches; this is not an exhaustive security assessment. See the [release checklist](docs/RELEASE_CHECKLIST.md).

## Historical portfolio release preparation — 23 October

Full suite rerun: **95 passed, 0 failed, 0 skipped in 65.63 seconds**. JUnit XML reports 95 tests, 0 failures, 0 errors and 0 skipped. Command: `..\..\work\.venv\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\release-tests.xml`.

No application code or tests changed during release preparation. `pip check` passed, the synthetic CSV matched the seed-42 generator exactly, and all 1,800 rows passed validation. Git ignore rules were tested with an external temporary Git directory; the project was uninitialized and unstaged at that review (it now has initial commit `63176f6`). No push, publication, deployment or user-data modification occurred. See [release checklist](docs/RELEASE_CHECKLIST.md) for the proposed first commit and manual publishing commands.

## Latest reliability follow-up

Result of the prior reliability follow-up: **95 passed, 0 failed, 0 skipped in 67.35 seconds**. JUnit XML confirms 95 tests, 0 failures, 0 errors and 0 skipped.

The unchanged existing suite first passed **90 tests, 0 failures, 0 skips in 54.28 seconds**. Five additional regression cases verify the five-status denominator, synthetic notices on all three analytical pages, and saved-upload persistence across two fresh application processes. No genuine test failures surfaced; no application code or existing assertions needed changing.

Commands run from the project folder:

```powershell
..\..\work\.venv\Scripts\python.exe -m pytest -q -ra
..\..\work\.venv\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\reliability-tests.xml
..\..\work\.venv\Scripts\python.exe scripts\audit_metrics.py
..\..\work\.venv\Scripts\python.exe -m pip check
Get-FileHash data\bookings.db
(Invoke-WebRequest 'http://127.0.0.1:8501/_stcore/health').Content
```

Status reconciliation from read-only SQL: 372 Confirmed + 998 Completed + 325 Cancelled + 62 Pending + 43 No-show = 1,800. Cancellation rate: 325 / 1,800 = 18.0556%, displayed as 18.1%. The independent metric audit still reconciles all eight KPIs; SQLite integrity is `ok`, with 0 foreign-key violations. Dependency check: no broken requirements.

The live dashboard displays the synthetic warning and the expected metrics; HTTP health is `ok`, with no captured browser console errors. Existing widget tests verify all four sidebar sections, imports and filter/export consistency. Source review found real implementations behind the custom buttons, not placeholders. Destructive reset behavior was exercised only in temporary databases.

The persistence test uploads a four-row CSV into a temporary app, then runs the complete app via AppTest in two separate Python processes. Each startup finds the saved snapshot with four bookings and booking value 1,000.00; the database hash remains unchanged. This verifies application startup across process boundaries without stopping the user's server; it is not a power-failure or abrupt-crash durability test.

The live DB hash remained `672760AC61EDF01101B8AEBBCF9F226D4135502FFF1DB66B30A026257EB7C495`. No live data was deleted or changed, and no deployment was attempted. README run/test/setup instructions were retained and extended with status and persistence troubleshooting.

## Previous audit result

Result at the previous audit: **90 passed, 0 failed, 0 skipped in 54.66 seconds**.

```powershell
..\..\work\.venv\Scripts\python.exe -m pytest -q --tb=short
```

The pre-audit suite had 52 passes and 0 failures (13.53 seconds). The audit added 38 cases, reproduced defects before fixing them, and reran the complete suite. See [AUDIT_REPORT.md](AUDIT_REPORT.md) for defects, formula assumptions, filter/export checks and verification boundaries.

Additional verified checks:

- Read-only Decimal reconciliation: all eight live KPIs match within 0.000001.
- All 1,800 canonical demo records match the supplied CSV.
- SQLite integrity: `ok`; foreign-key violations: 0.
- `pip check`: no broken requirements; offline requirements install dry-run succeeded.
- `compileall`: completed successfully for app, source, scripts and tests.
- Live HTTP health endpoint: `ok`; updated app reloaded with no captured browser console errors.
- Live DB hash **unchanged** before and after audit: `672760AC61EDF01101B8AEBBCF9F226D4135502FFF1DB66B30A026257EB7C495`.
- No live reset, upload, data deletion, deployment or publication was performed.

## Historical initial-build verification

Environment: Windows, Python 3.12.14. Exact direct dependency versions are recorded in `requirements-tested.txt`.

## Automated tests

Command run from the project folder:

```powershell
..\..\work\.venv\Scripts\python.exe -m pytest -q
```

Final full-suite result: **52 passed in 16.13 seconds; 0 failures**.

The initial run had 49 passes and one failure: the room-share insight selected only one leader for a tie. The implementation now reports all tied leaders, and the complete suite was rerun successfully with two additional UI import tests.

Coverage includes deterministic KPI totals, cancellation denominators, inclusive date filtering, combined category filters, empty selections, missing cost handling, invalid dates/numbers/statuses, aliases, duplicate/conflicting identifiers, PII-column exclusion, malformed files, CSV and XLSX parsing, export values, spreadsheet formula neutralization, database round trips, duplicate-import protection, persistent audit records, reset confirmation, preservation of uploaded snapshots, all four Streamlit pages, filtered empty states, and reviewed/duplicate/malformed UI uploads.

## Runtime checks

- Generated the included 1,800-row synthetic CSV using seed 42.
- Initialized `data/bookings.db` successfully with the synthetic snapshot.
- Started the real Streamlit server on loopback port 8501.
- HTTP `/_stcore/health` returned `ok`.
- Inspected the dashboard in the in-app browser at laptop and mobile viewport widths. Adjusted KPI wrapping after observing truncation in a narrow window.

No cloud deployment was performed. Browser inspection is a responsive smoke check, not exhaustive coverage of every browser/device. Automated UI tests use temporary databases and do not alter the working demo database. No real hotel dataset was present in the initial workspace.
