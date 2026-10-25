# Publication review — 25 October 2026

Latest local run: **164 passed, 0 failed, 0 skipped, 0 pytest warnings in 206.04 seconds**. See [TEST_RESULTS.md](../TEST_RESULTS.md).

## Decision and remaining cleanup

Local verification and the intended release contents are reviewed below. **Resolve the tracked pager-help artifact before publication.** The file `t -qpython -m pytest -q` is already tracked, contains terminal `less` help text and is unrelated to the project. Omitting it from `git add` does not remove it from a push. It has not been removed or untracked because the user has not approved that action. No credentials were detected in this file by the limited scan.

The supplied cleanup commands stop tracking it while preserving the local file. They do not rewrite history; the artifact remains in earlier commits. No history rewrite is proposed for this harmless generated text.

## Intended commit contents

| Files | Reason |
|---|---|
| app.py; src/analytics.py; src/advanced_analytics.py; src/charts.py; src/exports.py | Existing Version 2.0 dashboard, numerical correction, cancellation comparisons and five-sheet reporting |
| tests/test_database_exports.py; tests/test_advanced_analytics.py; tests/test_advanced_exports.py; tests/test_advanced_ui.py | Updated workbook contract and analytics/export/UI regressions |
| README.md; TEST_RESULTS.md; docs/DATA_GUIDE.md; docs/RELEASE_CHECKLIST.md | Setup, metric definitions, limitations and actual verification evidence |
| docs/PORTFOLIO_CASE_STUDY.md; docs/RESUME_PROJECT_ENTRY.md; docs/PUBLICATION_REVIEW.md | Reproducible synthetic findings, interview material and publication instructions |
| Six explicit PNGs below | Four current page captures plus two historical captures referenced by verification documentation |

The synthetic CSV, MIT license, requirements, scripts, public Streamlit settings and GitHub Actions workflow are already tracked and unchanged. They remain part of the repository without restaging. Do not add local databases, uploads, exports, environments, logs or test XML. The full intended list below includes no broad directory staging or force-add.

## Privacy and reproducibility review

The only public data/export/database candidate is `data/sample_hotel_bookings.csv`. Its canonical records exactly match the seeded generator. All case-study channel counts, rates, Wilson bounds, cancelled values and KPI monetary figures were reproduced; all four README image paths resolve to valid PNG files. The synthetic and non-causal limitations are explicit. Existing screenshots are synthetic-only or an empty import form.

No common private-key/GitHub/AWS/OpenAI token patterns were found in current public candidates or reachable local Git history. No database/workbook/environment file was found in the inspected reachable-history paths. No tracked ignored files or public candidates above 1 MB were found. These are bounded checks, not a guarantee against every secret format or undiscovered private text. Remote-only history was not fetched or inspected. Review staged files manually before publication.

Git exclusions cover representative DB, environment, private-upload, secret and workbook paths. Live data was preserved. Remote CI and broader browser/platform, accessibility, load and security testing remain pending; do not add a passing CI badge until a real run succeeds.

## Commands after explicit approval

Run these in PowerShell. Nothing below was executed by this review. First navigate to the existing repository and verify the destination:

```powershell
Set-Location 'C:\Users\devpa\Documents\Codex\2026-10-23\files-pasted-by-the-user-you\outputs\booking-analytics'
git status --short
git branch --show-current
git remote -v
```

Expected branch: `main`. Expected origin: `https://github.com/DevPanwar003/stayscope-booking-analytics.git`. Do not reinitialize Git or replace the remote.

**Only after approving removal from version control:** preserve the local artifact, ignore it and stage its removal from the repository tree:

```powershell
Add-Content -LiteralPath .gitignore -Value '/t -qpython -m pytest -q'
git rm --cached -- 't -qpython -m pytest -q'
git add -- .gitignore
```

Stage the exact intended files:

```powershell
$releaseFiles = @(
    "README.md"
    "TEST_RESULTS.md"
    "app.py"
    "src/analytics.py"
    "src/advanced_analytics.py"
    "src/charts.py"
    "src/exports.py"
    "tests/test_database_exports.py"
    "tests/test_advanced_analytics.py"
    "tests/test_advanced_exports.py"
    "tests/test_advanced_ui.py"
    "docs/DATA_GUIDE.md"
    "docs/RELEASE_CHECKLIST.md"
    "docs/PORTFOLIO_CASE_STUDY.md"
    "docs/RESUME_PROJECT_ENTRY.md"
    "docs/PUBLICATION_REVIEW.md"
    "docs/screenshots/overview.png"
    "docs/screenshots/cancellations-portfolio.png"
    "docs/screenshots/dataset.png"
    "docs/screenshots/quality.png"
    "docs/screenshots/cancellations.png"
    "docs/screenshots/cancellation-details.png"
)
git add -- $releaseFiles

git diff --cached --check
git diff --cached --stat
git diff --cached --name-status
git --no-pager diff --cached
git status --short
```

Confirm the index contains only the listed files, `.gitignore`, and the pager artifact's removal. If unrelated changes are already staged, stop and review them before committing. Inspect the six image files visually as well as the text diff.

After approving that staged review:

```powershell
git commit -m "Prepare StayScope 2.0 analytics and portfolio release"
git show --stat --oneline HEAD
git push --dry-run origin main
git push -u origin main
```

The dry-run contacts GitHub but does not publish a commit. If the push is rejected because remote history differs, stop and reconcile it; do not force-push or reset away changes. After publication, inspect both Windows and Ubuntu Python 3.12 jobs under GitHub Actions → Python tests. Add repository topics and a description, and confirm image rendering on GitHub. Do not describe this as a deployed application.
