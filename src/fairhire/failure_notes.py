"""Attach evidence and a plain explanation to each failure case, by fixed rules.

The explanations only state facts that can be checked in the data: which field
changed, which resume lines a keyword matched, and how many pieces the
embedding method split each text into. They never guess at hidden causes.
"""

from __future__ import annotations

from typing import Any, Optional

from fairhire.rank_embedding import MiniLMEncoder
from fairhire.rank_keyword import competency_level
from fairhire.render_resumes import render_text
from fairhire.schemas import Rubric, VariantRecord


METHOD_PLAIN = {"keyword": "keyword counting", "embedding": "meaning-matching",
                "embedding_sectioned": "section-by-section matching", "llm_rubric": "the AI marker"}
FIELD_PLAIN = {"name": "name", "career break": "career break", "institution": "university",
               "formatting": "section order"}


def _label(sample: VariantRecord) -> str:
    return f"{sample.base_resume_id} (a {sample.qualification_tier.value} candidate for job {sample.job_id})"


def _group(g: str) -> str:
    ethnicity, gender = g.split("_")
    return f"{ethnicity.capitalize()} {gender} name"


def _made(v: bool) -> str:
    return "made the top 4" if v else "missed the top 4"


def changed_field(a: VariantRecord, b: VariantRecord) -> dict[str, str]:
    """Human-readable description of what differs between two variants."""
    ra, rb = a.resume, b.resume
    if ra.identity.name != rb.identity.name:
        return {"field": "name", "a": ra.identity.name or "", "b": rb.identity.name or ""}
    if ra.career_breaks != rb.career_breaks:
        brk = (rb.career_breaks or ra.career_breaks)[0]
        return {"field": "career break", "a": "none" if not ra.career_breaks else brk.label,
                "b": f"{brk.label} {brk.start} to {brk.end}" if rb.career_breaks else "none"}
    if ra.education[0].institution != rb.education[0].institution:
        return {"field": "institution", "a": ra.education[0].institution, "b": rb.education[0].institution}
    if ra.render_options != rb.render_options:
        return {"field": "formatting", "a": ", ".join(ra.render_options.section_order),
                "b": ", ".join(rb.render_options.section_order)}
    return {"field": "none", "a": "", "b": ""}


def _chunk_note(encoder: Optional[MiniLMEncoder], method: str, a: VariantRecord, b: VariantRecord) -> Optional[str]:
    if encoder is None or method != "embedding":
        return None
    na, nb = len(encoder.chunks(render_text(a.resume))), len(encoder.chunks(render_text(b.resume)))
    if na != nb:
        return (f"Part of this jump is not about the change itself: the model reads about 250 words at a time, and "
                f"the change made the text read in {nb} piece{'s' if nb > 1 else ''} instead of {na}.")
    return None


def explain(case: dict[str, Any], variants: dict[str, VariantRecord], rubrics: dict[str, Rubric],
            encoder: Optional[MiniLMEncoder]) -> dict[str, Any]:
    rubric = rubrics[case["job_id"]]
    if case["kind"] == "tier_inversion":
        hi, lo = variants[case["higher_tier"]["sample_id"]], variants[case["lower_tier"]["sample_id"]]
        rows = []
        for comp in rubric.competencies:
            lh, _ = competency_level(hi.resume, comp)
            ll, lines = competency_level(lo.resume, comp)
            rows.append({"competency": comp.name, "higher_tier_level": lh, "lower_tier_level": ll,
                         "lower_tier_lines": lines})
        text = (f"With {METHOD_PLAIN[case['method']]}, {_label(lo)} scored {case['margin']:.1f} points higher than "
                f"{_label(hi)}, so the weaker candidate was ranked above the stronger one.")
        if case["method"] == "keyword":
            beats = [r for r in rows if r["lower_tier_level"] > r["higher_tier_level"]]
            if beats:
                r = beats[0]
                quote = r["lower_tier_lines"][0] if r["lower_tier_lines"] else "a skills-list entry"
                text += (f" It gave the weaker candidate credit for {r['competency']} because of the line "
                         f"\"{quote.rstrip('.')}\".")
        return {**case, "explanation": text, "evidence": rows}
    if case["kind"].startswith("largest_") or case["kind"] == "shortlist_flip":
        if "by_group" in case:
            ids = [v["sample_id"] for v in case["by_group"].values()]
            short = [g for g, v in case["by_group"].items() if v["shortlisted"]]
            text = (f"With {METHOD_PLAIN[case['method']]}, {_label(variants[ids[0]])} made the top 4 under "
                    f"{len(short)} of the 6 names ({', '.join(_group(g) for g in short) or 'none'}) and missed it under "
                    f"the others. Only the name was different.")
            return {**case, "explanation": text, "changed": {"field": "name"}}
        a, b = variants[case["a"]["sample_id"]], variants[case["b"]["sample_id"]]
        field = changed_field(a, b)
        gap = case.get("gap", (case["b"]["score"] or 0) - (case["a"]["score"] or 0))
        text = (f"{_label(a)}: changing the {FIELD_PLAIN.get(field['field'], field['field'])} from \"{field['a']}\" "
                f"to \"{field['b']}\" moved the {METHOD_PLAIN[case['method']]} score by {gap:+.1f} points.")
        if case["kind"] == "shortlist_flip":
            text += f" Before the change the candidate {_made(case['a']['shortlisted'])}; after it, they {_made(case['b']['shortlisted'])}."
        note = _chunk_note(encoder, case["method"], a, b)
        return {**case, "explanation": text + (f" {note}" if note else ""), "changed": field}
    return case
