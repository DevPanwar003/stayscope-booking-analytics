# First portfolio release checklist

Prepared locally on 23 October 2026. Nothing has been committed, pushed, deployed or published. The project is not yet a Git repository. A separate disposable Git directory under the workspace's `work/` folder was used solely to verify exclusions; it is not part of this release.

## Verified release evidence

- Full existing suite rerun: **95 passed, 0 failed, 0 skipped in 65.63 seconds**; JUnit XML confirms the counts.
- `pip check`: no broken requirements; bounded requirements and tested direct versions are retained.
- Sample CSV: exactly matches `generate_sample()` at seed 42; 1,800 accepted rows and no validation issues. Only synthetic booking fields are included, without guest contact columns.
- MIT license already present and preserved. No environment variables are required; no `.env.example` was added.
- Application code and interface unchanged for release preparation. README reorganized; detailed schema/metric notes preserved in `docs/DATA_GUIDE.md`.
- Live database hash unchanged: `672760AC61EDF01101B8AEBBCF9F226D4135502FFF1DB66B30A026257EB7C495`.

## Security and privacy review

Reviewed upload parsing, validation, SQL, rendering, export logic and configuration. Database values use bound parameters; static schema SQL contains no user input. `unsafe_allow_html` is used only for static CSS, not uploaded text. Exports neutralize formula-like text and escape Excel control characters. Demo reset requires typed confirmation and uses a transaction. Upload filenames do not select filesystem paths; original upload bytes are not written as arbitrary files.

No hardcoded credential was found in the reviewed application/configuration. This is a source review and existing regression-test evidence, not a professional penetration test or a dependency vulnerability scan. `pip check` verifies dependency compatibility, not vulnerability status.

Known boundaries: no authentication or encrypted database, no public-hosting hardening, and no compressed-workbook resource isolation. Treat this as a local application for trusted files. Recognized fields and filenames can contain private information; excluding unknown columns is not full anonymization. A `.gitignore` is not a substitute for inspecting staged files and images.

Verified exclusions include the live DB and SQLite sidecars, arbitrary CSV/XLSX files, `.env` variants, Streamlit secrets, credential JSON files, private key files, virtual environments and caches. The public Streamlit configuration and `data/sample_hotel_bookings.csv` remain eligible. Future private source files or screenshots with arbitrary names still require manual review. Do not use `git add -f` to bypass these protections.

## Proposed first-commit files

Commit these paths, after reviewing their contents:

```text
.gitignore
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

## Inspect, initialize and create the first commit

Commands below are for you to execute after reviewing the release. They were **not** executed against the project during preparation.

```powershell
cd "C:\Users\devpa\Documents\Codex\2026-10-23\files-pasted-by-the-user-you\outputs\booking-analytics"

# Check first. Currently this reports that the folder is not a Git repository.
git rev-parse --show-toplevel
Get-Content .gitignore
Get-Content README.md

# Run only if the check above finds no existing repository or parent repository.
git init -b main

git status --short --untracked-files=all
git status --short --ignored
git check-ignore -v data/bookings.db .env .env.local .streamlit/secrets.toml
git ls-files --others --exclude-standard

# Explicit paths: do not use `git add .` or `git add -f` for this first release.
git add -- .gitignore .streamlit/config.toml README.md LICENSE requirements.txt requirements-tested.txt pytest.ini app.py src/*.py scripts/*.py tests/*.py data/sample_hotel_bookings.csv docs/DATA_GUIDE.md docs/RELEASE_CHECKLIST.md AUDIT_REPORT.md TEST_RESULTS.md IMPLEMENTATION_PLAN.md

git diff --cached --check
git diff --cached --stat
git diff --cached --name-only
git diff --cached
git status --short

# Inspect existing identity; do not overwrite it automatically.
git config --get user.name
git config --get user.email

# After checking the entire staged diff:
git commit -m "Initial portfolio release: StayScope Booking Intelligence"
git log -1 --oneline
```

For a new repository, `git diff` has no baseline until files are staged; `git diff --cached` is the review of the proposed first commit. If the identity checks are empty, set only this repository's identity with your chosen public name and email before committing:

```powershell
git config --local user.name (Read-Host 'Commit author name')
git config --local user.email (Read-Host 'Commit email or GitHub noreply address')
```

If Git was initialized after this document was prepared, skip initialization and inspect its current branch, status and log instead. Do not reset history or overwrite an existing remote. If an unintended file is staged before the first commit, `git rm --cached -- path/to/file` removes it from the index while leaving the local file intact; review exclusions before continuing.

## Publishing later — explicit user action only

First review the staged/committed files for secrets and create an **empty** GitHub repository named `stayscope-booking-intelligence` in your chosen account. Do not initialize it with another README, license or gitignore. Choose public visibility only when you are ready to publish the portfolio.

After the first commit exists, run:

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
2. Review the first-commit file list and choose your commit identity and GitHub destination.
3. Verify a clean installation in CI before claiming cross-machine portability. Current tests used the installed Windows/Python 3.12 environment; no remote CI, production deployment, load test or penetration test has run.

Portfolio description: **StayScope is a Python hotel booking intelligence platform combining audited CSV/Excel ingestion, transactional SQLite storage, interactive dashboards and filter-consistent reports. Its synthetic demo and 95-test suite demonstrate transparent business metrics, data-quality handling and reliable application behavior.**
