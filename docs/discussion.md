---
run_id: run-1.0.0
variants_sha256_prefix: 40d518c174a74410
status: first draft written by Claude after reading the results; to be reviewed and rewritten by the applicant
---
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
