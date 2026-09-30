# Human reference labels

Not collected in version 1.0.0 (decided on 30 Sep 2026). The relevance results use the intended tiers instead, and
this is stated as a limitation. The steps below are kept so it can be done in a later version.

To add them:

1. Run `python scripts/make_scoring_sheet.py`. It writes `scoring_sheet_blank.csv` and `resumes_to_score.md`
   (resumes without names, in shuffled order, with the rubrics and without intended tiers).
2. Score every row 0 to 3 in a copy of the sheet, before looking at any model result. Save it here as
   `applicant_scores.csv`.
3. If a second reviewer scores a subset, save theirs as `second_reviewer_scores.csv` and record disagreements in
   `docs/manual_review_log.md` instead of averaging them away.
4. Run `python scripts/analyse_results.py`, then `generate_report.py` and `build_site.py`.
