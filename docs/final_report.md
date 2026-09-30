# FairHire Audit: final report

Run `run-1.0.0`, benchmark v1.0.0, generated from `results/summary.json`. Every number below is produced by `scripts/generate_report.py`; none is typed by hand.

All resumes, names and employers in this study are fictional.

## Question

When two resumes show the same job-relevant evidence, do keyword, embedding and LLM ranking methods give them the same score? Which method agrees best with a rubric written before any method was run? Do anonymisation or evidence-only scoring reduce the differences, and at what cost?

## Setup

- 24 fictional base resumes across 3 job families, 2 jobs per family, 2 resumes per intended tier per job.
- 480 scored variants and 864 controlled pairs: 48 career break, 48 formatting, 48 university, 720 name.
- Methods and mitigations run: Embedding; Embedding, anonymised; Embedding, evidence only; Sectioned embedding; Sectioned embedding, anonymised; Keyword.
- LLM rubric scorer: not run.
- Shortlist = top 4 of the 8 candidates for a job. Material gap = more than 2.0 points. Confidence intervals: 10000 bootstrap resamples of base resumes (seed 7). Tests: Wilcoxon signed-rank on one value per base resume, Holm adjustment across all 20 testable comparisons.
- Code version `no-git:src-sha256:4517d80d19e19e0a`, config SHA-256 `7e26ca0f16d7c529`, variants SHA-256 `40d518c174a74410`, run at 2026-09-30T04:12:57Z.

## Headline findings

**Names changed the scores of one method.** When only the name changed, the meaning-matching method's score for the same resume moved by 4.3 points out of 100 on average (up to 9.2). That was enough to change who made the top 4 in 15% of cases. No gender or group was consistently favoured. The scores moved around rather than leaning one way.

**Hiding names fixed the name problem only.** When names and emails were hidden before scoring, the name effect disappeared and the method got better at ranking stronger candidates above weaker ones (83% of the time before, 90% after). A career break still moved scores by 1.5 points on average, and changing the section order by 1.9.

**Keyword counting never moved, but it can be fooled.** Keyword counting gave the same score to both versions in every pair. It ranked stronger candidates above weaker ones 96% of the time, against 83% for meaning-matching. Its word lists and the intended strong-to-weak order were written by the same person, which helps it. It still made mistakes: it once ranked a weaker candidate above a stronger one because of a single matching word (case F27 on the Mistakes page).

## 1. How much does one changed field move the score?

Mean absolute gap in points with 95% confidence interval, signed gap for the main comparison, share of resume-job rows with a material gap, shortlist flip rate, and Holm-adjusted p-value.

| Field | Method | Mean abs gap (95% CI) | Signed gap (95% CI) | Material | Flips | p (Holm) |
|---|---|---|---|---|---|---|
| Name | Embedding | 4.32 (3.80 to 4.87) | spread | 96% | 15% |  |
| Name | Embedding, anonymised | 0.00 (0.00 to 0.00) | spread | 0% | 0% |  |
| Name | Embedding, evidence only | 0.00 (0.00 to 0.00) | spread | 0% | 0% |  |
| Name | Sectioned embedding | 0.46 (0.42 to 0.51) | spread | 0% | 2% |  |
| Name | Sectioned embedding, anonymised | 0.00 (0.00 to 0.00) | spread | 0% | 0% |  |
| Name | Keyword | 0.00 (0.00 to 0.00) | spread | 0% | 0% |  |
| Career break | Embedding | 1.18 (0.74 to 1.83) | +0.38 (-0.23 to +1.17) | 15% | 4% | 1.000 |
| Career break | Embedding, anonymised | 1.52 (1.12 to 1.96) | +0.16 (-0.56 to +0.89) | 29% | 6% | 1.000 |
| Career break | Embedding, evidence only | 0.00 (0.00 to 0.00) | +0.00 (+0.00 to +0.00) | 0% | 0% | not testable |
| Career break | Sectioned embedding | 0.73 (0.58 to 0.90) | +0.49 (+0.23 to +0.75) | 0% | 6% | 0.020 |
| Career break | Sectioned embedding, anonymised | 0.73 (0.58 to 0.90) | +0.49 (+0.23 to +0.75) | 0% | 4% | 0.020 |
| Career break | Keyword | 0.00 (0.00 to 0.00) | +0.00 (+0.00 to +0.00) | 0% | 0% | not testable |
| University | Embedding | 0.41 (0.30 to 0.52) | +0.13 (-0.06 to +0.31) | 0% | 2% | 1.000 |
| University | Embedding, anonymised | 0.37 (0.27 to 0.49) | +0.03 (-0.16 to +0.21) | 0% | 0% | 1.000 |
| University | Embedding, evidence only | 0.00 (0.00 to 0.00) | +0.00 (+0.00 to +0.00) | 0% | 0% | not testable |
| University | Sectioned embedding | 0.27 (0.20 to 0.35) | -0.18 (-0.29 to -0.06) | 0% | 0% | 0.077 |
| University | Sectioned embedding, anonymised | 0.27 (0.20 to 0.35) | -0.18 (-0.29 to -0.06) | 0% | 0% | 0.077 |
| University | Keyword | 0.00 (0.00 to 0.00) | +0.00 (+0.00 to +0.00) | 0% | 0% | not testable |
| Formatting | Embedding | 2.02 (1.44 to 2.65) | -0.76 (-1.70 to +0.21) | 33% | 8% | 1.000 |
| Formatting | Embedding, anonymised | 1.94 (1.33 to 2.72) | -0.65 (-1.71 to +0.30) | 35% | 2% | 1.000 |
| Formatting | Embedding, evidence only | 0.00 (0.00 to 0.00) | +0.00 (+0.00 to +0.00) | 0% | 0% | not testable |
| Formatting | Sectioned embedding | 0.53 (0.39 to 0.68) | -0.47 (-0.65 to -0.30) | 0% | 0% | < 0.001 |
| Formatting | Sectioned embedding, anonymised | 0.53 (0.39 to 0.68) | -0.47 (-0.65 to -0.30) | 0% | 2% | < 0.001 |
| Formatting | Keyword | 0.00 (0.00 to 0.00) | +0.00 (+0.00 to +0.00) | 0% | 0% | not testable |

Name comparisons by direction (positive means the first group scored higher):

| Method | Comparison | Signed gap (95% CI) | p (Holm) |
|---|---|---|---|
| Embedding | female minus male | -0.05 (-0.43 to +0.32) | 1.000 |
| Embedding | malay minus chinese | +0.71 (+0.18 to +1.20) | 0.272 |
| Embedding | indian minus chinese | +0.92 (+0.18 to +1.66) | 0.638 |
| Embedding | indian minus malay | +0.22 (-0.53 to +0.96) | 1.000 |
| Sectioned embedding | female minus male | -0.03 (-0.08 to +0.01) | 1.000 |
| Sectioned embedding | malay minus chinese | +0.05 (-0.05 to +0.14) | 1.000 |
| Sectioned embedding | indian minus chinese | +0.06 (+0.00 to +0.13) | 1.000 |
| Sectioned embedding | indian minus malay | +0.01 (-0.07 to +0.11) | 1.000 |
| Keyword | female minus male | +0.00 (+0.00 to +0.00) | not testable |
| Keyword | malay minus chinese | +0.00 (+0.00 to +0.00) | not testable |
| Keyword | indian minus chinese | +0.00 (+0.00 to +0.00) | not testable |
| Keyword | indian minus malay | +0.00 (+0.00 to +0.00) | not testable |

## 2. Agreement with the intended tiers

| Method | Tier accuracy (95% CI) | Spearman, mean (range over jobs) | Pairs |
|---|---|---|---|
| Embedding | 0.83 (0.76 to 0.89) | 0.71 (0.34 to 0.93) | 144 |
| Embedding, anonymised | 0.90 (0.84 to 0.94) | 0.82 (0.34 to 0.98) | 144 |
| Embedding, evidence only | 0.85 (0.79 to 0.91) | 0.77 (0.49 to 0.98) | 144 |
| Sectioned embedding | 0.89 (0.83 to 0.94) | 0.81 (0.59 to 0.98) | 144 |
| Sectioned embedding, anonymised | 0.89 (0.83 to 0.94) | 0.81 (0.59 to 0.98) | 144 |
| Keyword | 0.96 (0.92 to 0.99) | 0.94 (0.85 to 0.99) | 144 |

The reference is the intended tier set by the resume author. Human reference labels have not been collected yet (see `data/human_labels/README.md`).

## 3. Stability

| Method | Top-4 overlap after reformatting | Rank agreement after reformatting | Runs | Spread across runs |
|---|---|---|---|---|
| Embedding | 0.80 | 0.90 | 1 | deterministic |
| Embedding, anonymised | 0.93 | 0.96 | 1 | deterministic |
| Embedding, evidence only | 1.00 | 1.00 | 1 | deterministic |
| Sectioned embedding | 1.00 | 1.00 | 1 | deterministic |
| Sectioned embedding, anonymised | 1.00 | 1.00 | 1 | deterministic |
| Keyword | 1.00 | 1.00 | 1 | deterministic |

## 4. Mitigations

| Method | Tier accuracy | Name spread | Career break | University | Formatting |
|---|---|---|---|---|---|
| Embedding | 0.83 | 4.32 | 1.18 | 0.41 | 2.02 |
| Embedding, anonymised | 0.90 | 0.00 | 1.52 | 0.37 | 1.94 |
| Embedding, evidence only | 0.85 | 0.00 | 0.00 | 0.00 | 0.00 |
| Sectioned embedding | 0.89 | 0.46 | 0.73 | 0.27 | 0.53 |
| Sectioned embedding, anonymised | 0.89 | 0.00 | 0.73 | 0.27 | 0.53 |
| Keyword | 0.96 | 0.00 | 0.00 | 0.00 | 0.00 |

## 5. Hypotheses

**H1, identical evidence gets similar scores.** Held for Sectioned embedding, Keyword in the sense that no pair moved by more than 2.0 points. Did not hold for Embedding, where at least one changed field moved scores by more than 2.0 points. Even gaps below the threshold still flipped some shortlist decisions for Sectioned embedding, because candidates close to the cut-off can swap places.

**H2, structured scoring agrees more with the rubric than raw similarity.** Keyword rubric scoring reached tier accuracy 0.96 against 0.83 for whole-resume embedding (intervals do not overlap). Scoring only the extracted evidence with embedding gave 0.85. Supported in direction, with the caveat that the intended tiers and the keyword lists share an author.

**H3, anonymisation reduces identity gaps but not proxies.** Name spread after anonymisation: 0.00 points. Career-break and university changes still moved scores after anonymisation in 2 of 2 comparisons. Consistent with H3.

**H4, LLM scoring is persuasive but less stable.** Not tested: the LLM scorer was not run for this version.

## 6. Failure cases

Selected by fixed rules in `src/fairhire/evaluate.py`, not by hand.

- **F01** (Embedding, SE-01): With meaning-matching, SE-R04 (a borderline candidate for job SE-01) scored 26.0 points higher than SE-R07 (a good candidate for job SE-01), so the weaker candidate was ranked above the stronger one.
- **F02** (Embedding, MA-01): MA-R06 (a borderline candidate for job MA-01): changing the name from "Muhammad Hafiz Rahman" to "Priya Nair" moved the meaning-matching score by +9.2 points.
- **F03** (Embedding, SE-01): SE-R07 (a good candidate for job SE-01): changing the career break from "none" to "Career break 2022-02 to 2023-01" moved the meaning-matching score by +8.1 points. Part of this jump is not about the change itself: the model reads about 250 words at a time, and the change made the text read in 2 pieces instead of 1.
- **F04** (Embedding, DA-02): DA-R02 (a borderline candidate for job DA-02): changing the university from "Singapore University of Social Sciences" to "Nanyang Technological University" moved the meaning-matching score by +1.4 points.
- **F05** (Embedding, DA-01): With meaning-matching, DA-R02 (a good candidate for job DA-01) made the top 4 under 4 of the 6 names (Malay female name, Malay male name, Indian female name, Indian male name) and missed it under the others. Only the name was different.
- **F06** (Embedding, DA-01): With meaning-matching, DA-R03 (a borderline candidate for job DA-01) made the top 4 under 5 of the 6 names (Chinese female name, Chinese male name, Malay female name, Malay male name, Indian female name) and missed it under the others. Only the name was different.
- **F07** (Embedding, DA-02): With meaning-matching, DA-R03 (a weak candidate for job DA-02) made the top 4 under 1 of the 6 names (Malay male name) and missed it under the others. Only the name was different.
- **F08** (Embedding, DA-01): DA-R05 (a good candidate for job DA-01): changing the section order from "summary, experience, education, skills" to "summary, skills, experience, education" moved the meaning-matching score by -4.7 points. Before the change the candidate made the top 4; after it, they missed the top 4.
- **F09** (Embedding, DA-01): With meaning-matching, DA-R05 (a good candidate for job DA-01) made the top 4 under 5 of the 6 names (Chinese male name, Malay female name, Malay male name, Indian female name, Indian male name) and missed it under the others. Only the name was different.
- **F10** (Embedding, DA-01): DA-R06 (a strong candidate for job DA-01): changing the career break from "none" to "Career break 2021-02 to 2022-01" moved the meaning-matching score by -2.1 points. Before the change the candidate made the top 4; after it, they missed the top 4.
- **F11** (Embedding, DA-01): DA-R06 (a strong candidate for job DA-01): changing the section order from "summary, experience, education, skills" to "summary, skills, experience, education" moved the meaning-matching score by -1.9 points. Before the change the candidate made the top 4; after it, they missed the top 4.
- **F12** (Embedding, DA-01): With meaning-matching, DA-R07 (a borderline candidate for job DA-01) made the top 4 under 5 of the 6 names (Chinese male name, Malay female name, Malay male name, Indian female name, Indian male name) and missed it under the others. Only the name was different.
- **F13** (Embedding, DA-02): DA-R08 (a borderline candidate for job DA-02): changing the section order from "summary, experience, education, skills" to "summary, skills, experience, education" moved the meaning-matching score by -5.7 points. Before the change the candidate made the top 4; after it, they missed the top 4.
- **F14** (Embedding, MA-02): With meaning-matching, MA-R08 (a weak candidate for job MA-02) made the top 4 under 1 of the 6 names (Indian female name) and missed it under the others. Only the name was different.
- **F15** (Embedding, SE-01): SE-R03 (a good candidate for job SE-01): changing the career break from "none" to "Career break 2022-09 to 2023-08" moved the meaning-matching score by +0.8 points. Before the change the candidate missed the top 4; after it, they made the top 4.
- **F16** (Embedding, SE-01): SE-R06 (a weak candidate for job SE-01): changing the university from "Singapore Institute of Technology" to "Nanyang Technological University" moved the meaning-matching score by +0.7 points. Before the change the candidate missed the top 4; after it, they made the top 4.
- **F17** (Embedding, SE-01): SE-R06 (a weak candidate for job SE-01): changing the section order from "summary, experience, education, skills" to "summary, skills, experience, education" moved the meaning-matching score by -3.1 points. Before the change the candidate made the top 4; after it, they missed the top 4.
- **F18** (Embedding, SE-01): With meaning-matching, SE-R06 (a weak candidate for job SE-01) made the top 4 under 3 of the 6 names (Chinese female name, Malay male name, Indian female name) and missed it under the others. Only the name was different.
- **F19** (Sectioned embedding, MA-01): With section-by-section matching, MA-R04 (a weak candidate for job MA-01) scored 17.7 points higher than MA-R07 (a borderline candidate for job MA-01), so the weaker candidate was ranked above the stronger one.
- **F20** (Sectioned embedding, MA-01): MA-R04 (a weak candidate for job MA-01): changing the name from "Muhammad Hafiz Rahman" to "Priya Nair" moved the section-by-section matching score by +0.7 points.
- **F21** (Sectioned embedding, MA-01): MA-R08 (a weak candidate for job MA-01): changing the career break from "none" to "Career break 2021-03 to 2022-02" moved the section-by-section matching score by +1.9 points.
- **F22** (Sectioned embedding, MA-01): MA-R06 (a borderline candidate for job MA-01): changing the university from "Singapore Institute of Technology" to "Nanyang Technological University" moved the section-by-section matching score by -0.7 points.
- **F23** (Sectioned embedding, DA-01): DA-R03 (a borderline candidate for job DA-01): changing the career break from "none" to "Career break 2023-06 to 2024-05" moved the section-by-section matching score by +1.3 points. Before the change the candidate missed the top 4; after it, they made the top 4.
- **F24** (Sectioned embedding, MA-01): MA-R05 (a good candidate for job MA-01): changing the career break from "none" to "Career break 2023-01 to 2023-12" moved the section-by-section matching score by +1.1 points. Before the change the candidate missed the top 4; after it, they made the top 4.
- **F25** (Sectioned embedding, SE-01): SE-R08 (a weak candidate for job SE-01): changing the career break from "none" to "Career break 2022-03 to 2023-02" moved the section-by-section matching score by +0.8 points. Before the change the candidate missed the top 4; after it, they made the top 4.
- **F26** (Sectioned embedding, SE-01): With section-by-section matching, SE-R08 (a weak candidate for job SE-01) made the top 4 under 1 of the 6 names (Malay female name) and missed it under the others. Only the name was different.
- **F27** (Keyword, MA-02): With keyword counting, MA-R08 (a weak candidate for job MA-02) scored 10.0 points higher than MA-R01 (a borderline candidate for job MA-02), so the weaker candidate was ranked above the stronger one. It gave the weaker candidate credit for CRM and campaign platforms because of the line "Visit about 15 customers a week and record orders in the company CRM".

## 7. Discussion

### What the results suggest

Whole-resume embedding was the only method whose scores moved by more than the material threshold when a single field changed. Names produced the widest spread: across six names, the same resume's score usually varied by several points. The direction of the name effect was not consistent: no gender or naming-group comparison stayed significant after adjusting for the number of tests. So on this data the problem looks more like instability tied to names than a steady preference for one group. For a hiring team the practical result is similar either way: whether a borderline candidate reaches the shortlist can depend on their name.

Formatting moved whole-resume embedding scores more on average than a career break did. Moving the skills section above the experience section is not something a recruiter would expect to change a ranking, so this is a useful reminder that "the model read the resume" hides a lot of sensitivity to layout.

The largest single career-break gap came from how the text was split into pieces for the model, not from the break itself. Adding one line pushed the resume over the model's 256 word-piece limit, so the last skills line became a separate piece. This was found by the automatic failure-case check and is kept as a result rather than fixed after the fact, because changing the method after seeing the results would bias the comparison. A fairer chunking rule is a candidate for the next benchmark version.

The section-aware embedding was much steadier than whole-resume embedding. Its gaps were small, but some were statistically detectable (the career break and the layout change), and small gaps still flipped a few shortlist decisions for candidates near the cut-off. "Statistically detectable" and "large enough to matter" are different questions, and this benchmark shows both.

Anonymisation removed the name effect completely, as it must, and it also raised tier accuracy for whole-resume embedding. Career-break and formatting effects remained. The evidence-only version removed every gap, but only because it throws away the fields being tested. That is a design choice with a cost: anything the rubric keyword lists do not cover is dropped too.

The keyword baseline had the best agreement with the intended tiers and no pair gaps at all. That should not be read as "keyword matching is best". The intended tiers and the keyword lists were written by the same person, so they share assumptions. The keyword method also made a clear mistake: it credited a sales resume with CRM platform experience because the word CRM appeared in a sentence about recording orders. Independent human labels are the next step for a fair relevance comparison.

### What this does not show

These are fictional resumes and a small set, chosen so that every pair can be inspected by hand. Nothing here says that any real employer, tool or person discriminates. The LLM scorer was built and tested but not run, so hypothesis H4 is untested.

### Next experiments

1. Run the LLM rubric scorer when budget or GPU access allows (about USD 10 for the main comparison, USD 31 for everything).
2. Collect blind rubric scores from the applicant and a second reviewer, and compare methods against them.
3. Test a chunking rule that does not depend on where a single line falls, as benchmark version 1.1.
4. Add more base resumes per tier so that smaller effects can be estimated with tighter intervals.

## Reproduce

```bash
pip install -r requirements.txt
python scripts/download_model.py
python scripts/build_dataset.py
python scripts/run_experiment.py
python scripts/analyse_results.py
python scripts/generate_report.py
python scripts/build_site.py
pytest
```
