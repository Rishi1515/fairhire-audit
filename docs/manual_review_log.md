# Manual review log

Written by the applicant, not generated. Each entry records what was actually checked, what was wrong and what
changed. An entry stays empty until the review has really happened.

**Status for benchmark v1.0.0:** design decisions D1 to D8 reviewed on 30 Sep 2026. Blind human scoring
left out of this version by decision on 30 Sep 2026. Still to do: reading the job, rubric and resume files in full,
checking a sample of pairs, and the interpretation.

## 1. Jobs, rubrics and transformation rules

- Date reviewed: 30 Sep 2026 (decisions only)
- Reviewer: Rishi Varma
- Files checked: the eight design decisions in `docs/review/REVIEW_CHECKLIST.md`, walked through one at a time.
  The job, rubric and resume files have not been read in full yet.
- Problems found: none raised.
- Changes made: no data or rule changes. The LLM rubric scorer was moved to future work (see D7).
- Decisions:
  - D1 name test scope: kept gender crossed with Chinese, Malay and Indian naming conventions.
  - D2 pronouns: kept out.
  - D3 career break rule: kept (12 months before the latest role, earlier history shifted back).
  - D4 university sets: kept NUS and NTU against SIT and SUSS.
  - D5 what rubrics ignore: kept (university name and industry experience are not scored).
  - D6 tiers per job: kept.
  - D7 models: kept all-MiniLM-L6-v2 for meaning-matching. The LLM rubric scorer is not run in this version
    because there is no budget for API calls and no access to GPU compute right now; it stays built and tested
    and is listed as future work.
  - D8 shortlist of 4 and 2-point threshold: kept.

## 2. The 24 base resumes

- Date reviewed:
- Resumes checked:
- Problems found:
- Changes made:

## 3. Sample of generated pairs

- Date reviewed:
- Pairs checked (ids):
- Any pair where more than the intended field changed:
- Changes made:

## 4. Human reference labels

- Decision (30 Sep 2026): not done in version 1.0.0. Relevance is measured against the intended levels set when the
  resumes were written, and this is stated as a limitation. Blind human scoring is listed as future work in the README.

## 5. Interpretation

- Date reviewed:
- Claims checked against results files:
- Wording changed (bias, fairness, significance, improvement):
- docs/discussion.md rewritten in own words: yes / no
