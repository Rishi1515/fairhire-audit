"""Generate counterfactual variants and pairs from canonical resumes.

Every variant is built by code from the same structured record. Nothing is
rewritten by a language model. Each base resume produces ten variants:

* ``REF``        reference identity, standard formatting
* ``NAME-<grp>`` the same resume under a name from each other name group (5)
* ``GAP``        a 12-month career break inserted before the most recent role
* ``INST-HIGH``  first education entry at a higher-ranked university
* ``INST-COMP``  first education entry at a comparison university
* ``FMT-ALT``    alternative section order and bullet character

Each variant is scored against both jobs in its family, giving 20 samples per
base resume and 480 samples in total.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fairhire.integrity import check_pair, content_hash
from fairhire.schemas import (CanonicalResume, CareerBreak, Identity, JobDescription, PairRecord, RenderOptions,
                              Resume, TransformationType, VariantRecord, to_months)

T = TransformationType


def from_months(index: int) -> str:
    """Inverse of ``schemas.to_months``."""
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def stable_rng(seed: int, key: str) -> random.Random:
    """A random generator that depends only on the seed and a text key."""
    digest = hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


@dataclass(frozen=True)
class Variant:
    code: str
    transformation: TransformationType
    value: str
    resume: Resume


# --------------------------------------------------------------------------- identities


def make_identity(group: str, person: dict[str, str], name_cfg: dict[str, Any]) -> Identity:
    first, last = person["first"], person["last"]
    name = f"{last} {first}" if group in name_cfg.get("surname_first", []) else f"{first} {last}"
    email = name_cfg["email_pattern"].format(first=first.replace(" ", "").lower(),
                                             last=last.replace(" ", "").lower())
    return Identity(name=name, email=email)


def assign_names(index: int, name_cfg: dict[str, Any]) -> tuple[str, dict[str, Identity]]:
    """Pick one name per group for base resume number ``index``.

    The reference group rotates through the groups so that every group is the
    reference equally often, and names within a group rotate so that no single
    name carries a group's result.
    """
    groups = list(name_cfg["name_bank"])
    reference_group = groups[index % len(groups)]
    identities = {}
    for g in groups:
        bank = name_cfg["name_bank"][g]
        identities[g] = make_identity(g, bank[(index // len(groups) + index) % len(bank)], name_cfg)
    return reference_group, identities


# --------------------------------------------------------------------------- transformations


def with_identity(resume: Resume, identity: Identity) -> Resume:
    return Resume.model_validate({**resume.model_dump(), "identity": identity.model_dump()})


def insert_career_gap(resume: Resume, months: int, label: str) -> Resume:
    """Insert a career break before the most recent role, keeping total experience the same.

    Every earlier role and every education entry moves back by ``months``, and
    the break fills the space they leave behind.
    """
    data = resume.model_dump()
    shift = lambda d: from_months(to_months(d) - months)  # noqa: E731
    for role in data["experience"][1:]:
        role["start"], role["end"] = shift(role["start"]), shift(role["end"])
    for edu in data["education"]:
        edu["start"], edu["end"] = shift(edu["start"]), shift(edu["end"])
    original_prev_end = to_months(resume.experience[1].end)
    data["career_breaks"] = [CareerBreak(label=label, start=from_months(original_prev_end - months + 1),
                                         end=from_months(original_prev_end)).model_dump()]
    out = Resume.model_validate(data)
    if out.months_of_experience("2100-01") != resume.months_of_experience("2100-01"):
        raise AssertionError("career gap changed total experience")
    return out


def swap_institution(resume: Resume, institution: str) -> Resume:
    data = resume.model_dump()
    data["education"][0]["institution"] = institution
    return Resume.model_validate(data)


def with_format(resume: Resume, fmt: dict[str, Any]) -> Resume:
    data = resume.model_dump()
    data["render_options"] = RenderOptions(section_order=tuple(fmt["section_order"]),
                                           bullet=fmt["bullet"]).model_dump()
    return Resume.model_validate(data)


def build_variants(base: CanonicalResume, index: int, cfg: dict[str, Any]) -> tuple[list[Variant], str]:
    """Return the ten variants of one base resume and its reference name group."""
    tcfg = cfg["transformations"]
    seed = cfg["seeds"]["generation"]
    reference_group, identities = assign_names(index, tcfg["name_cue"])
    plain = Resume.model_validate(base.model_dump())
    plain = with_format(plain, tcfg["formatting"]["standard"])
    ref = with_identity(plain, identities[reference_group])

    variants = [Variant("REF", T.NONE, f"reference ({reference_group})", ref)]
    for group, identity in identities.items():
        if group != reference_group:
            variants.append(Variant(f"NAME-{group}", T.NAME_CUE, group, with_identity(plain, identity)))
    gap = tcfg["career_gap"]
    variants.append(Variant("GAP", T.CAREER_GAP, f"{gap['length_months']} month break",
                            insert_career_gap(ref, gap["length_months"], gap["label"])))
    rng = stable_rng(seed, base.resume_id)
    inst = tcfg["institution"]
    variants.append(Variant("INST-HIGH", T.INSTITUTION, "higher_ranked",
                            swap_institution(ref, rng.choice(inst["higher_ranked"]))))
    variants.append(Variant("INST-COMP", T.INSTITUTION, "comparison",
                            swap_institution(ref, rng.choice(inst["comparison"]))))
    variants.append(Variant("FMT-ALT", T.FORMATTING, "alternative", with_format(ref, tcfg["formatting"]["alternative"])))
    return variants, reference_group


def pair_specs(reference_group: str, groups: list[str]) -> list[tuple[T, str, str]]:
    """(transformation, code_a, code_b) for every pair of one base resume.

    Signed gaps are always b minus a: name pairs are ordered as in the config,
    gap pairs are GAP minus REF, institution pairs are HIGH minus COMP, and
    formatting pairs are ALT minus REF.
    """
    code = lambda g: "REF" if g == reference_group else f"NAME-{g}"  # noqa: E731
    specs = [(T.NAME_CUE, code(a), code(b)) for a, b in itertools.combinations(groups, 2)]
    specs += [(T.CAREER_GAP, "REF", "GAP"), (T.INSTITUTION, "INST-COMP", "INST-HIGH"), (T.FORMATTING, "REF", "FMT-ALT")]
    return specs


def build_benchmark(resumes: dict[str, CanonicalResume], jobs: dict[str, JobDescription],
                    cfg: dict[str, Any]) -> tuple[list[VariantRecord], list[PairRecord], dict[str, str]]:
    """Build every variant record and pair record, checking integrity as it goes."""
    groups = list(cfg["transformations"]["name_cue"]["name_bank"])
    version = cfg["benchmark_version"]
    records: list[VariantRecord] = []
    pairs: list[PairRecord] = []
    reference_groups: dict[str, str] = {}
    for index, rid in enumerate(sorted(resumes)):
        base = resumes[rid]
        variants, ref_group = build_variants(base, index, cfg)
        reference_groups[rid] = ref_group
        by_code = {v.code: v for v in variants}
        group_of = {("REF" if g == ref_group else f"NAME-{g}"): g for g in groups}
        for job_id in sorted(base.intended_tier):
            for v in variants:
                value = group_of.get(v.code, v.value) if v.code == "REF" else v.value
                records.append(VariantRecord(
                    sample_id=f"{rid}-{job_id}-{v.code}", base_resume_id=rid, job_id=job_id,
                    qualification_tier=base.intended_tier[job_id], transformation_type=v.transformation,
                    transformation_value=value, generation_version=version,
                    content_hash=content_hash(v.resume, v.transformation), resume=v.resume))
            for n, (ttype, a, b) in enumerate(pair_specs(ref_group, groups)):
                check_pair(by_code[a].resume, by_code[b].resume, ttype)
                pairs.append(PairRecord(pair_id=f"{rid}-{job_id}-P{n:02d}", base_resume_id=rid, job_id=job_id,
                                        transformation_type=ttype, sample_a=f"{rid}-{job_id}-{a}",
                                        sample_b=f"{rid}-{job_id}-{b}"))
    return records, pairs, reference_groups


def write_benchmark(records: list[VariantRecord], pairs: list[PairRecord], reference_groups: dict[str, str],
                    out_dir: Path, cfg: dict[str, Any], source_hashes: dict[str, str]) -> dict[str, Any]:
    """Write variants.jsonl, pairs.jsonl and a manifest. Output is byte-for-byte reproducible."""
    out_dir.mkdir(parents=True, exist_ok=True)
    variants_text = "".join(r.model_dump_json() + "\n" for r in records)
    pairs_text = "".join(p.model_dump_json() + "\n" for p in pairs)
    (out_dir / "variants.jsonl").write_text(variants_text, encoding="utf-8")
    (out_dir / "pairs.jsonl").write_text(pairs_text, encoding="utf-8")
    manifest = {
        "benchmark_version": cfg["benchmark_version"],
        "generation_seed": cfg["seeds"]["generation"],
        "n_base_resumes": len(reference_groups),
        "n_samples": len(records),
        "n_pairs": len(pairs),
        "pairs_by_type": {t.value: sum(p.transformation_type == t for p in pairs) for t in T if t != T.NONE},
        "reference_name_group": reference_groups,
        "variants_sha256": hashlib.sha256(variants_text.encode()).hexdigest(),
        "pairs_sha256": hashlib.sha256(pairs_text.encode()).hexdigest(),
        "source_files_sha256": source_hashes,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest
