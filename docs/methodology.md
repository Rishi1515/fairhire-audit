# Methodology

This describes how benchmark version 1.0.0 was built, scored and analysed. Results are in
`docs/final_report.md`, which is generated from the result files.

## Research questions

1. When qualifications are unchanged, how often does changing one background field change the score or the shortlist?
2. Which ranking method agrees best with a rubric written before any model was run?
3. How stable is each method across repeated runs and small formatting changes?
4. Do anonymisation or evidence-only scoring reduce counterfactual gaps without hurting relevance?

## Hypotheses

- H1: Counterfactual pairs receive similar scores when job-relevant evidence is identical.
- H2: Structured competency scoring agrees with the rubric more closely than raw embedding similarity.
- H3: Anonymisation reduces gaps tied to explicit identity cues, but may not remove proxy effects.
- H4: LLM scoring gives persuasive explanations but is less stable than the deterministic methods.

## Why a Singapore setting

The best-known audits of AI resume screening (Bloomberg 2024; Wilson and Caliskan 2024; Armstrong et al. 2024)
use US naming conventions and US race categories. This benchmark sets all jobs and candidates in Singapore and uses
Chinese, Malay and Indian naming conventions alongside gender. Singapore's Workplace Fairness Act, which covers
hiring decisions, is expected to come into force at the end of 2027 (Herbert Smith Freehills Kramer). This project
makes no legal findings; the Act is context for why employers may ask this question.

## Data

| Component | Version 1.0.0 |
|---|---|
| Job families | Data analyst, software engineer, marketing analyst |
| Jobs | 2 per family, 6 in total (`data/jobs/`) |
| Rubrics | 1 per job, 6 or 7 weighted competencies (`data/rubrics/`) |
| Base resumes | 8 per family, 24 in total (`data/canonical_resumes/`) |
| Intended tiers | Strong, good, borderline, weak; exactly 2 resumes per tier for every job |
| Variants | 10 per base resume, each scored against 2 jobs: 480 samples |
| Pairs | 864: 720 name, 48 career break, 48 university, 48 formatting |

Base resumes are stored as YAML and validated against typed schemas (`src/fairhire/schemas.py`). A base resume has
no name, email or pronouns. Universities were spread across tiers on purpose, so that strong resumes are not all at
highly ranked universities.

## Transformations

All variants are produced by code from the structured record (`src/fairhire/generate_pairs.py`). No language
model rewrites any resume.

| Test | What changes | What must stay identical |
|---|---|---|
| Name | Name and the email built from it | Everything else |
| Career break | A 12-month "Career break" line before the most recent role; earlier roles and education move back 12 months | Total months of experience, all bullets, skills, grades |
| University | Institution of the first education entry | Degree, subject, grade, dates, coursework |
| Formatting | Section order and bullet character | All text |

Six names are used per resume: a female and a male name in each of the Chinese, Malay and Indian naming conventions,
drawn from a bank of three names per group. Each group is the reference name for exactly four base resumes.

Every pair is checked by `src/fairhire/integrity.py`: the permitted fields are deleted from both records, the rest is
hashed, and the build fails unless the hashes match and the full records differ. Generation is deterministic; the
manifest records SHA-256 hashes of the source files and outputs.

## Ranking methods

**Keyword baseline** (`rank_keyword.py`). Matches only the aliases listed in each rubric competency. Level 1 if the
skill appears only in the summary, skills, education or certifications; level 2 for one experience or project line;
level 3 for two or more. Score = 100 x sum(weight x level / 3).

**Embedding** (`rank_embedding.py`). sentence-transformers/all-MiniLM-L6-v2 through ONNX Runtime on CPU. The job
description and resume are split at line breaks into pieces of at most 254 word pieces, embedded with mean pooling,
averaged by length and compared with cosine similarity. Score = 100 x cosine, floored at 0. The model file is pinned
by SHA-256 and a test checks it reproduces the model's published reference similarities.

**Section-aware embedding.** Each resume section (header, summary, experience, skills, education) is compared with
the job separately and the similarities are combined with weights 0.05, 0.10, 0.50, 0.25 and 0.10.

**LLM rubric scorer** (`rank_llm.py`). Returns a level, exact quotes and missing evidence per competency, plus
uncertainty and a recommendation, as validated JSON. The score uses the same weighted formula as the keyword
baseline. Every call is cached with its prompt, parameters, raw reply and parser status. It was not run for
version 1.0.0 because no API key was available; see `docs/model_prompts.md`.

## Mitigations

- **Anonymised:** name and email are replaced by "Candidate" before scoring.
- **Evidence only:** the method reads only the resume lines that match each rubric competency, grouped by competency.

## Human reference labels

Not collected yet. `scripts/make_scoring_sheet.py` creates a blank sheet and an anonymised, shuffled copy of the
resumes. When `data/human_labels/applicant_scores.csv` exists, the analysis adds rank correlations against it.
Until then, relevance is measured against the intended tiers, which were set by the resume author.

## Metrics and statistics

| Metric | Meaning |
|---|---|
| Signed and absolute pair gap | Score of the changed version minus the original, and its size |
| Name spread | Highest minus lowest score across the six names for one resume and job |
| Share material | Share of resume-job rows with a gap above 2 points |
| Flip rate | Share of resume-job rows where the top-4 shortlist decision changes |
| Tier accuracy | Share of cross-tier candidate pairs ordered correctly (ties count half) |
| Spearman | Rank correlation with intended tier order, per job |
| Formatting top-4 overlap | Jaccard overlap of shortlists under the two layouts |
| Run spread | Standard deviation across repeated LLM runs |
| Evidence validity | Share of LLM quotes found in the resume text |

Each base resume appears in many rows, so gaps are averaged within each base resume first. Confidence intervals
come from 10,000 bootstrap resamples of the 24 base resumes (seed 7). Direction is tested with a Wilcoxon
signed-rank test on the 24 per-resume values, and p-values are Holm-adjusted across all tests. A gap is called
detectable only when the adjusted p-value is below 0.05.

## Validity safeguards

- Seeds for generation, bootstrap and LLM ordering are fixed in `config/experiment.yaml`.
- The benchmark was generated and hashed before any method was run; results record the benchmark hash and are
  rejected by the analysis if it does not match.
- LLM prompt examples use a fixture resume that is not part of the benchmark.
- No method sees intended tiers, design notes or the other member of a pair.
- Both members of a pair go through the same rendering and preprocessing functions.
- Failure cases are selected by fixed rules, and headline sentences are chosen by rules from the numbers.

## References

Armstrong, Lena, et al. "The Silicon Ceiling: Auditing GPT's Race and Gender Biases in Hiring." *arXiv*, 2024, arxiv.org/abs/2405.04412.

Herbert Smith Freehills Kramer. "Singapore: Workplace Fairness Act to Take Effect End of 2027." *HSF Kramer Notes*, 2025, www.hsfkramer.com/notes/employment/2025-posts/singapore-workplace-fairness-act-to-take-effect-end-of-2027.

Wilson, Kyra, and Aylin Caliskan. "Gender, Race, and Intersectional Bias in Resume Screening via Language Model Retrieval." *Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society*, 2024, arxiv.org/abs/2407.20371.

Yin, Leon, et al. "OpenAI GPT Sorts Resume Names With Racial Bias, Test Shows." *Bloomberg*, Mar. 2024, www.bloomberg.com/graphics/2024-openai-gpt-hiring-racial-discrimination/.
