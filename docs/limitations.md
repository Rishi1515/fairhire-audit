# Limitations

**Synthetic setting.** All resumes and jobs are fictional and written in one consistent style. Real resumes vary far
more in length, language, layout and quality, and methods may behave differently on them.

**Small sample.** 24 base resumes, 6 jobs. This is enough to see large effects and to inspect every pair by hand,
but intervals are wide and small effects cannot be ruled out.

**Relevance reference is not independent.** The intended tier of each resume was set by the same author who wrote
the rubrics and the keyword aliases. Agreement with intended tiers therefore favours the keyword method. Blind human
labels from the applicant and a second reviewer are needed for a fair comparison.

**Names as proxies.** Names are used as cues a reader might associate with gender and ethnicity. They do not
represent anyone's actual identity, and three names per group cannot capture how varied real names are.

**Career break side effect.** Keeping total experience constant means shifting earlier dates back, so the
graduation year also moves back one year. Any career-break effect may partly reflect that weak age cue.

**University labels.** The two groups differ in international ranking visibility. The label says nothing about the
quality of any institution, and some degree subjects may not be offered at every university used.

**Chunking.** The embedding model reads at most 256 word pieces at a time. Resumes are split at line breaks, so a
single added line can change how a resume is split. At least one large gap in this run came partly from this.

**Model and version dependence.** Results hold for this embedding model, this keyword design and these
settings. Other models, including larger embedding models and LLMs, may behave differently.

**LLM scorer not run.** Hypothesis H4 is untested in version 1.0.0. The scorer is built and tested but was not run
because there was no API budget or GPU access; it is listed as future work in the README.

**Association, not discrimination.** A score gap in a synthetic benchmark shows how a method responds to a changed
field. It is not evidence of unlawful discrimination by any person, company or product.

**Review in progress.** The benchmark was drafted by Claude. The applicant confirmed the eight design decisions on
30 Sep 2026; reading the resumes and rubrics in full, blind human scoring and the final interpretation are still to
do (see `docs/manual_review_log.md`).
