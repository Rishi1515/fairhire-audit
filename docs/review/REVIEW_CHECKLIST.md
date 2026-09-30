# Review checklist

The first run used defaults chosen by Claude. These are the reviews that make the design yours. Record each one in
`docs/manual_review_log.md` in your own words. If you change a data or config file, bump `benchmark_version` in
`config/experiment.yaml` and re-run the pipeline, so old and new results are never mixed.

## 1. Jobs and rubrics (`docs/review/review_sheet.md`)

- [ ] Each posting reads like a real Singapore job ad at about two years' experience.
- [ ] Every requirement is covered by a competency, or its absence is intentional.
- [ ] The weights match what you think matters for the job.
- [ ] "Counts as evidence" describes something you can see in a resume.
- [ ] No employer name is a real company. Search each one quickly.

## 2. Base resumes (same file)

- [ ] Dates and career stories make sense.
- [ ] Each resume fits its intended tier for both jobs (read the design notes).
- [ ] Weak resumes are realistic, not caricatures.
- [ ] Each degree subject is plausibly offered at every university in the swap set.

## 3. Generated pairs

- [ ] Open 10 pairs in the website's pair inspector across all four fields and check that only the highlighted lines differ.

## 4. Decisions made as defaults

All eight were confirmed by Rishi Varma on 30 Sep 2026. D7 changed: the LLM scorer is deferred to future work.

| # | Decision | Default used in v1.0.0 | Where |
|---|---|---|---|
| D1 | Name test scope | Gender crossed with Chinese, Malay and Indian naming conventions. This is wider than the brief's "name or gender cue", so it needs your explicit yes. | `config/experiment.yaml` |
| D2 | Pronouns | Not included; uncommon on Singapore resumes. | same |
| D3 | Career break rule | 12 months, labelled "Career break", before the most recent role; earlier history shifted back. Side effect: graduation year moves one year earlier. | same |
| D4 | University sets | NUS and NTU against SIT and SUSS, described as ranking visibility, not quality. | same |
| D5 | What rubrics ignore | University name and domain experience are not scored. | `data/rubrics/` |
| D6 | Tiers per job | Each resume has a tier for each job in its family. | `data/canonical_resumes/` |
| D7 | Models | Embedding all-MiniLM-L6-v2; LLM Claude Haiku 4.5, temperature 1.0, 5 repeats. | `config/models.yaml` |
| D8 | Shortlist and threshold | Top 4 of 8; a gap above 2 points counts as material. | `config/experiment.yaml` |

## 5. Human labels

Left out of version 1.0.0 by decision on 30 Sep 2026; listed as future work in the README. The tools to do it later
are in `data/human_labels/`.

## 6. Interpretation

- [ ] Read `docs/final_report.md` and rewrite `docs/discussion.md` in your own words.
- [ ] Check that every use of "bias", "fair", "significant" or "improve" matches the numbers.
