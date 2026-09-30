"""Plain-text rendering is the input to every ranking method, so it must be exact."""

from fairhire.data_io import load_resumes
from fairhire.render_resumes import format_month, render_text
from fairhire.schemas import CareerBreak


def test_format_month():
    assert format_month("2023-03") == "Mar 2023"
    assert format_month(None) == "Present"


def test_career_break_is_placed_in_date_order():
    resume = load_resumes()["DA-R01"]
    with_break = resume.model_copy(update={
        "career_breaks": [CareerBreak(label="Career break", start="2022-01", end="2022-06")]})
    text = render_text(with_break)
    newer = text.index("Data Analyst, Sembawang Mart")
    brk = text.index("Career break | Jan 2022 - Jun 2022")
    older = text.index("Junior Data Analyst, Straits Parcel Logistics")
    assert newer < brk < older


def test_filled_identity_is_rendered():
    resume = load_resumes()["DA-R02"]
    ident = resume.identity.model_copy(update={"name": "Test Name", "email": "test.name@example.com"})
    text = render_text(resume.model_copy(update={"identity": ident}))
    assert text.splitlines()[0] == "Test Name"
    assert "test.name@example.com" in text.splitlines()[1]
