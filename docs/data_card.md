# Data card: FairHire Audit benchmark v1.0.0

## Summary

A small synthetic benchmark of 24 fictional resumes and 6 fictional job descriptions set in Singapore, with 480
programmatically generated variants and 864 controlled pairs. It is built to test whether resume-ranking methods
change their scores when only a name, a career break, a university or the layout changes.

## Everything is fictional

- No resume describes a real person. No real resume was copied or adapted.
- Names are combinations of common given names and surnames, chosen so that no full name belongs to a well-known person.
- Every email uses example.com, a domain reserved for examples. Every phone number is the same placeholder.
- Employers in job descriptions and resumes are invented names. Universities are real institutions, used only as
  labels in the university test; no claim is made about their quality.

## Contents

| Path | Contents |
|---|---|
| `data/jobs/*.yaml` | 6 job descriptions |
| `data/rubrics/*.yaml` | 6 rubrics: competencies, importance, weights, evidence rules, keyword aliases |
| `data/canonical_resumes/*.yaml` | 24 base resumes with intended tier per job and design notes |
| `data/generated_pairs/variants.jsonl` | 480 variant records (resume, job, tier, transformation, hash) |
| `data/generated_pairs/pairs.jsonl` | 864 pair records |
| `data/generated_pairs/manifest.json` | Counts, seeds and SHA-256 hashes |
| `data/rendered_pdf/*.pdf` | PDF versions of the 24 reference resumes, for reading only |
| `data/human_labels/` | Blank scoring sheet for blind human labels |

## Schema

Each base resume has: `resume_id`, `family`, `intended_tier` (per job), `generation_version`, `status`,
`design_notes`, `identity` (empty), `summary`, `experience` (employer, title, location, start, end, bullets),
`education` (institution, qualification, subject, start, end, grade, coursework), `skills`, `certifications`,
`projects`, `career_breaks` and `render_options`. Dates are `YYYY-MM`. Full definitions are in `src/fairhire/schemas.py`.

## Intended uses

- Testing whether a ranking method is consistent when only one controlled field changes.
- Comparing ranking methods and mitigations on the same inputs.
- Teaching and discussion of evaluation design for automated screening.

## Uses this data does not support

- Claims about any real employer, applicant tracking system or hiring decision.
- Training or tuning a model to screen real applicants.
- Legal conclusions about discrimination.
- Estimates of how often bias occurs in real hiring.

## Known limitations

- 24 base resumes is small; intervals are wide for small effects.
- Intended tiers were set by the resume author, who also wrote the rubrics and keyword aliases.
- Names act as cues for gender and ethnicity only as a reader might perceive them.
- The career-break transformation also moves the graduation year back by one year.
- Some degree subjects may not be offered at every university used in the swap.
- All text is in plain English with a consistent style, unlike real resumes.

## Review status

The jobs, rubrics, resumes and transformation rules were drafted by Claude. The applicant confirmed the design
decisions on 30 Sep 2026; the full read-through of jobs, rubrics and resumes is still to do. Reviews are recorded in
`docs/manual_review_log.md`.
