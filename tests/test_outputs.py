"""Human labels, report reproducibility and the website loader."""

import json
import re
import sys
from pathlib import Path

import pytest

from fairhire.data_io import REPO_ROOT, load_rubrics
from fairhire.evaluate import load_human_scores

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import build_site  # noqa: E402


def test_human_scores_use_the_rubric_formula(tmp_path):
    rubric = load_rubrics()["DA-01"]
    path = tmp_path / "labels.csv"
    rows = ["resume_id,job_id,competency_id,level"]
    rows += [f"DA-R01,DA-01,{c.competency_id},3" for c in rubric.competencies]
    rows += [f"DA-R02,DA-01,{c.competency_id}," for c in rubric.competencies]  # unscored, ignored
    path.write_text("\n".join(rows) + "\n")
    scores = load_human_scores(path, load_rubrics())
    assert scores == {("DA-R01", "DA-01"): pytest.approx(100.0)}


def test_human_scores_reject_out_of_range_levels(tmp_path):
    path = tmp_path / "labels.csv"
    path.write_text("resume_id,job_id,competency_id,level\nDA-R01,DA-01,sql,4\n")
    with pytest.raises(ValueError, match="0 to 3"):
        load_human_scores(path, load_rubrics())


def test_missing_label_file_means_no_labels(tmp_path):
    assert load_human_scores(tmp_path / "none.csv", load_rubrics()) == {}


def test_site_rejects_incompatible_results(tmp_path):
    path = tmp_path / "summary.json"
    path.write_text(json.dumps({"summary_version": "0"}))
    with pytest.raises(build_site.IncompatibleResultsError, match="summary_version"):
        build_site.load_summary(path)


def test_site_numbers_come_from_the_saved_results(tmp_path):
    summary_path = REPO_ROOT / "results" / "summary.json"
    if not summary_path.exists():
        pytest.skip("run the experiment and analysis first")
    out = build_site.build(summary_path, tmp_path)
    page = out.read_text(encoding="utf-8")
    blob = page.split('id="site-data">', 1)[1].split("</script>", 1)[0].replace("<\\/", "</")
    data = json.loads(blob)
    assert data["summary"] == json.loads(summary_path.read_text(encoding="utf-8"))
    template = (REPO_ROOT / "site_src" / "template.html").read_text(encoding="utf-8")
    script = template.split("</style>", 1)[1]  # page logic and markup, without the stylesheet
    # no result number is typed into the page: decimal values in the headlines appear only in the data
    numbers = set(re.findall(r"\d+\.\d+", " ".join(h["text"] for h in data["summary"]["headlines"])))
    assert numbers
    for value in numbers:
        assert not re.search(rf"(?<![\d.]){re.escape(value)}(?![\d])", script), value


def test_summary_is_reproducible_from_scores():
    """Re-running the analysis on the saved scores gives the same tables."""
    from fairhire.data_io import load_config
    from fairhire.reporting import build_summary

    summary_path = REPO_ROOT / "results" / "summary.json"
    if not summary_path.exists():
        pytest.skip("run the experiment and analysis first")
    saved = json.loads(summary_path.read_text(encoding="utf-8"))
    cfg = load_config()
    fresh = build_summary(REPO_ROOT / "results" / "scores.csv", saved["run"], saved["benchmark"], cfg["analysis"],
                          cfg["scope"]["shortlist_k"], cfg["seeds"]["bootstrap"])
    fresh = json.loads(json.dumps(fresh))
    assert fresh["gaps"] == saved["gaps"]
    assert fresh["relevance"] == saved["relevance"]
