# Quality audit verification — 23 October 2026

## Portfolio release preparation — latest run

Full suite rerun: **95 passed, 0 failed, 0 skipped in 65.63 seconds**. JUnit XML reports 95 tests, 0 failures, 0 errors and 0 skipped. Command: `..\..\work\.venv\Scripts\python.exe -m pytest -q -ra --junitxml=..\..\work\release-tests.xml`.

No application code or tests changed during release preparation. `pip check` passed, the synthetic CSV matched the seed-42 generator exactly, and all 1,800 rows passed validation. Git ignore rules were tested with an external temporary Git directory; the project remains uninitialized and unstaged. No push, publication, deployment or user-data modification occurred. See [release checklist](docs/RELEASE_CHECKLIST.md) for the proposed first commit and manual publishing commands.

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
