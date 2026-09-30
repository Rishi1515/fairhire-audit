# Interview notes

Plain-language notes for explaining the project. Check any number against `docs/final_report.md` before quoting it.

## Two-minute explanation

Companies use software to rank resumes. I wanted to know if those methods are consistent: if two resumes have
exactly the same skills and experience, do they get the same score?

I wrote 24 fictional resumes for six Singapore jobs, from strong to weak. Then code made copies of each resume where
only one thing changed: the name, a one-year career break, the university, or the order of the sections. That gave
864 pairs where I know the only difference.

I scored every copy with three methods. A keyword method that counts rubric skills. An embedding method that turns
the resume and the job ad into numbers and measures how close they are. And an LLM that scores against the rubric,
which I built and tested but have not run yet because it needs a paid key.

The main finding: the embedding method's score moved by several points just from the name, and that was enough to
change who made the shortlist in about one in seven cases. The direction was not consistent, so it looks more like
instability than a steady preference. Removing names fixed the name effect and even improved accuracy, but layout
and career-break effects stayed. The keyword method never moved, but it had its own failure: it thought a sales
resume had CRM software skills because the word CRM appeared.

## Likely questions

**Why fictional resumes?** Real resumes differ in many ways at once, so you cannot tell what caused a score change.
Fictional resumes let me change exactly one thing. It also avoids using anyone's personal data.

**How do you know only one thing changed?** Each pair goes through an automatic check: I delete the fields that are
allowed to change, hash the rest, and the build fails if the hashes differ.

**Is a gap of a few points a big deal?** On its own, maybe not. What matters is the shortlist: candidates near the
cut-off swap places, so the name decided the outcome for some of them.

**Did you find discrimination?** No, and the project does not claim that. It shows how methods respond to changed
fields on synthetic data. No gender or group difference was consistent after correcting for the number of tests.

**Why is the keyword method so accurate?** Partly because I designed the tiers and the keyword lists, so they agree
by construction. That is a limitation, and it is why I am collecting blind human labels.

**What was surprising?** The biggest career-break effect was caused by how the text was split into pieces for the
model: one extra line pushed it over the model's reading limit. I kept that result instead of quietly fixing it.

**What would you do next?** Run the LLM scorer, add blind human labels, fix the text-splitting rule as a new
version, and add more resumes per tier.

**What did you personally decide?** Fill this in after completing the reviews in `docs/manual_review_log.md`.
