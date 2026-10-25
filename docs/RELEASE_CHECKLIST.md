# Portfolio release checklist

## Version 2.0 update

Latest local verification: **164 passed, 0 failed, 0 skipped**, no warnings reported. All four pages were inspected in the Windows in-app browser; four genuine screenshots are included. Excel preserves its original worksheets and adds cancellation benchmarks, value bands and definitions. The downloaded workbook was inspected and reconciled. See [the verification record](../TEST_RESULTS.md).

- [x] Full suite and focused export checks executed locally on Python 3.12.14.
- [x] Desktop navigation/rendering and narrow Import & quality layout inspected.
- [x] Four synthetic-only/form screenshots captured and linked in README.
- [x] Existing push/PR/manual CI workflow reviewed; Windows/Ubuntu Python 3.12 matrix retained.
- [ ] Execute the updated code on GitHub Actions after user-approved commit/push.
- [ ] Additional browser engines, other machines, accessibility audit and load testing.
- [ ] Review the full diff and staged files before publishing. Nothing was staged, committed, pushed or deployed by this task.

The evidence below is historical and is superseded by this section where it differs.

## Historical first-release preparation

Updated 24 October 2026. The repository already has commit `63176f6` (`Initial release: StayScope booking analytics`), branch `main`, and an `origin` remote. This preparation did not create that commit or remote and did not stage, commit, push, deploy or publish anything. Do not initialize Git again or overwrite the remote.

## Follow-up preparation — 24 October 2026

The README now includes the intended audience, a roadmap, four explicitly pending screenshot placeholders, and Python 3.12-specific setup commands. `.github/workflows/tests.yml` was added for pushes, pull requests and manual dispatch. It installs the documented dependencies and runs tests plus demo initialization/reconciliation on Windows and Ubuntu with Python 3.12. Its repository permissions are read-only; checkout does not persist credentials. Workflow structure was reviewed locally; no remote workflow run is claimed. See [TEST_RESULTS.md](../TEST_RESULTS.md) for clean-environment results and precise completion status.

The workflow uses official [checkout](https://github.com/actions/checkout) and [setup-python](https://github.com/actions/setup-python) actions. Keeping application source at the repository root is required for its relative paths. No CI badge should be added until an actual GitHub run exists.

## Verified release evidence

- Full existing suite rerun: **95 passed, 0 failed, 0 skipped in 195.68 seconds**, with 75 NumPy timedelta deprecation warnings; JUnit XML confirms the counts.
- Fresh isolated Windows Python 3.12.14 environment: dependency installation succeeded; `pip check` passed. Full suite and real Streamlit HTTP startup passed. Demo initialization and all eight independent metric checks passed in a separate temporary copy. See `TEST_RESULTS.md` for commands and resolved versions.
- Pending: GitHub CI execution, genuine screenshots, other-machine/OS verification, load testing and independent security assessment. The current NumPy date-filter warnings remain a compatibility follow-up.
- Sample CSV: exactly matches `generate_sample()` at seed 42; 1,800 accepted rows and no validation issues. Only synthetic booking fields are included, without guest contact columns.
- MIT license already present and preserved. No environment variables are required; no `.env.example` was added.
- Application code and interface unchanged for release preparation. README reorganized; detailed schema/metric notes preserved in `docs/DATA_GUIDE.md`.
- Live database hash unchanged: `672760AC61EDF01101B8AEBBCF9F226D4135502FFF1DB66B30A026257EB7C495`.

## Security and privacy review

Reviewed upload parsing, validation, SQL, rendering, export logic and configuration. Database values use bound parameters; static schema SQL contains no user input. `unsafe_allow_html` is used only for static CSS, not uploaded text. Exports neutralize formula-like text and escape Excel control characters. Demo reset requires typed confirmation and uses a transaction. Upload filenames do not select filesystem paths; original upload bytes are not written as arbitrary files.

No hardcoded credential was found in the reviewed application/configuration. The current tracked file inventory contains no local database, private-upload directory, virtual environment or secret configuration. A tracked-file scan for common private-key and token patterns returned no matches; this is not an exhaustive secret scan. `git ls-files -ci --exclude-standard` returned no tracked ignored files. This is a source review and existing regression-test evidence, not a professional penetration test or a dependency vulnerability scan. `pip check` verifies dependency compatibility, not vulnerability status.

Known boundaries: no authentication or encrypted database, no public-hosting hardening, and no compressed-workbook resource isolation. Treat this as a local application for trusted files. Recognized fields and filenames can contain private information; excluding unknown columns is not full anonymization. A `.gitignore` is not a substitute for inspecting staged files and images.

Verified exclusions include the live DB and SQLite sidecars, arbitrary CSV/XLSX files, `.env` variants, Streamlit secrets, credential JSON files, private key files, virtual environments and caches. The public Streamlit configuration and `data/sample_hotel_bookings.csv` remain eligible. Future private source files or screenshots with arbitrary names still require manual review. Do not use `git add -f` to bypass these protections.

## Existing release files

The existing tracked release contains these paths; the workflow is newly proposed:

```text
.gitignore
.github/workflows/tests.yml
.streamlit/config.toml
README.md
LICENSE
requirements.txt
requirements-tested.txt
pytest.ini
app.py
src/__init__.py
src/analytics.py
src/charts.py
src/database.py
src/exports.py
src/sample.py
src/validation.py
scripts/audit_metrics.py
scripts/generate_sample.py
scripts/init_db.py
tests/conftest.py
tests/test_analytics.py
tests/test_app.py
tests/test_audit_regressions.py
tests/test_database_exports.py
tests/test_validation.py
data/sample_hotel_bookings.csv
docs/DATA_GUIDE.md
docs/RELEASE_CHECKLIST.md
AUDIT_REPORT.md
TEST_RESULTS.md
IMPLEMENTATION_PLAN.md
```

Do not include the DB, original private uploads, generated exports, temporary JUnit results, virtual environments or caches. Genuine screenshots can be added in a later commit after the README capture procedure and privacy review. Existing audit records describe earlier runs; `TEST_RESULTS.md` identifies the newest release verification.

## Inspect and create the next commit

Run these from the project folder after reviewing all changes. Git is already initialized; no `git init` is needed.

```powershell
git status --short --untracked-files=all
git diff --check
git diff -- .gitignore README.md TEST_RESULTS.md docs/RELEASE_CHECKLIST.md
Get-Content .github/workflows/tests.yml
git check-ignore -v data/bookings.db .env .env.local .streamlit/secrets.toml
# This should print nothing: ignored artifacts already tracked by Git.
git ls-files -ci --exclude-standard

git add -- .gitignore README.md TEST_RESULTS.md docs/RELEASE_CHECKLIST.md .github/workflows/tests.yml
git diff --cached --check
git diff --cached --stat
git diff --cached
git config --get user.name
git config --get user.email
# Commit only after reviewing the staged content and author identity.
git commit -m "Prepare portfolio documentation and CI verification"
git log -1 --oneline
```

These are manual instructions, not actions performed during preparation. Preserve existing identity, history and remote configuration. Do not stage databases, private uploads or temporary verification files.

## Publishing later — explicit user action only

First review the staged/committed files for secrets and create an **empty** GitHub repository named `stayscope-booking-intelligence` in your chosen account. Do not initialize it with another README, license or gitignore. Choose public visibility only when you are ready to publish the portfolio.

An `origin` remote already exists. Inspect its destination before any future publication; do not add or replace it blindly. Run only when you intend to publish:

```powershell
git status --short
git branch --show-current
git remote -v
$githubOwner = Read-Host 'GitHub username or organization owning the empty repository'

# Only if no origin remote already exists:
git remote add origin "https://github.com/$githubOwner/stayscope-booking-intelligence.git"
git remote -v

# Review origin and confirm the intended branch is main before transmitting:
git push -u origin main
```

The final command publishes/transmits committed content. It is provided as a future manual step, not authorization for an agent to execute it. If `origin` already exists, inspect it and reuse it only if it is the intended destination; do not replace it blindly. Do not force-push. No account name, remote or GitHub repository has been invented or created for you.

## Remaining release work

1. Capture and review the four real UI screenshots described in README.
2. Review the next-commit diff and verify the existing commit identity and GitHub destination.
3. Run the new workflow on GitHub after an explicitly approved push. Local installation evidence does not establish cross-machine compatibility. No remote CI, production deployment, load test or penetration test was performed in this review.

Portfolio description: **StayScope is a Python hotel booking intelligence platform combining audited CSV/Excel ingestion, transactional SQLite storage, interactive dashboards and filter-consistent reports. Its synthetic demo and 95-test suite demonstrate transparent business metrics, data-quality handling and reliable application behavior.**
