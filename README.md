# FairHire Audit

By Rishi Varma

When two resumes show the same job-relevant evidence, do automated ranking methods give them the same score?

This is a small, controlled benchmark. 24 fictional Singapore resumes are turned by code into 480 variants where
only one field changes: the name, a career break, the university or the layout. Keyword, embedding and LLM ranking
methods score every variant, and the analysis measures how much scores and shortlist decisions move. It also tests
two mitigations: anonymisation and scoring only the rubric-relevant evidence.

All resumes, names and employers are fictional. Results describe method behaviour on this synthetic set, not any
real hiring process.

## Results (benchmark v1.0.0)

The full tables, confidence intervals and failure cases are in [`docs/final_report.md`](docs/final_report.md),
generated from [`results/summary.json`](results/summary.json). The evidence browser is `site/index.html`.

The headline findings are produced by rules from the numbers; see the report for the exact wording and values.
In short:

- Whole-resume embedding scores moved by several points when only the name changed, enough to change some
  shortlist decisions. No consistent direction by gender or naming group survived correction for multiple tests.
- Anonymisation removed the name effect and did not reduce accuracy, but career-break and layout effects remained.
- The rubric keyword method never changed a score within a pair and matched the intended tiers best, partly by
  construction, and it was fooled by the word "CRM" in a sales resume.
- The LLM rubric scorer is implemented and tested but was not run in v1.0.0; it is listed under Future work.

## Quick start

Needs Python 3.11 or newer. No GPU or API key is needed.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_model.py     # 90 MB embedding model, checked by SHA-256
pytest                               # 117 tests
```

Small demonstration (2 resumes, a few seconds):

```bash
python scripts/run_experiment.py --demo
```

Full experiment (about a minute on a laptop):

```bash
python scripts/build_dataset.py      # variants, pairs, manifest (byte-for-byte reproducible)
python scripts/run_experiment.py     # results/scores.csv
python scripts/analyse_results.py    # results/tables, final_metrics.csv, summary.json
python scripts/generate_report.py    # docs/final_report.md, docs/model_prompts.md
python scripts/build_site.py         # site/index.html
```

Optional LLM scorer:

```bash
pip install -r requirements-llm.txt
python scripts/run_experiment.py --llm-cost    # estimate first
ANTHROPIC_API_KEY=... python scripts/run_experiment.py --llm
```

## Repository map

| Path | Contents |
|---|---|
| `config/` | Experiment settings, seeds, transformation rules, model identifiers |
| `data/jobs/`, `data/rubrics/` | 6 job descriptions and their weighted rubrics |
| `data/canonical_resumes/` | 24 base resumes with intended tiers |
| `data/generated_pairs/` | 480 variants, 864 pairs, manifest with hashes |
| `data/rendered_pdf/` | PDF copies of the reference resumes |
| `data/human_labels/` | Blank blind scoring sheet |
| `src/fairhire/` | Schemas, pair generation, integrity checks, ranking methods, metrics, reporting |
| `scripts/` | One script per pipeline step |
| `results/` | Raw scores, tables, summary, run metadata |
| `site_src/`, `site/` | Evidence browser template and built page |
| `docs/` | Methodology, data card, limitations, prompts, report, review log, interview notes |
| `tests/` | Pair integrity, parsing, scoring, anonymisation, metrics, reproducibility, site loader |

## Why each dependency is here

| Package | Used for |
|---|---|
| pydantic | Validating every data file against typed schemas |
| PyYAML | Readable data and config files |
| numpy, scipy | Bootstrap intervals, Wilcoxon tests, rank correlation |
| onnxruntime, tokenizers | Running the embedding model locally on CPU |
| reportlab | PDF copies of resumes |
| pytest | Tests |
| anthropic (optional) | LLM rubric scorer |

## Future work

These are planned but not part of version 1.0.0.

- **Run the AI marker (LLM rubric scorer).** It is built and tested but has not been run, because this version
  had no budget for API calls and no GPU access. Two routes: Claude Haiku 4.5 through the API (about US$10 for
  the main comparison with 5 repeats, about US$31 for every fix as well; `python scripts/run_experiment.py
  --llm-cost` prints the estimate), or an open model run on a GPU. This would test hypothesis H4: is the AI
  marker persuasive but less stable?
- **Blind human scores.** Score all 24 resumes against the rubrics without seeing results, ideally with a second
  person, and compare every method against them (`data/human_labels/`).
- **A fairer way to split long resumes.** The meaning-matching model reads about 250 words at a time; one large
  gap came from where a resume was split. Test a better splitting rule as version 1.1.
- **More resumes per level,** so smaller effects can be measured with tighter ranges.
- **Other models,** including larger embedding models.

## Limitations

Synthetic and small by design. Intended tiers were set by the same author as the rubrics. One embedding model.
The LLM scorer was not run. The design decisions were confirmed by the applicant; the resumes and rubrics are still being reviewed. See
[`docs/limitations.md`](docs/limitations.md).

## Licence

MIT. See `LICENSE`.
