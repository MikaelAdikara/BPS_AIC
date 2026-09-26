"""Juri relevansi (kode, tanpa model).

Kutipan yang lolos verifier membuktikan pembeli menulisnya, bukan bahwa ulasan itu mendukung
temuan ini. Setiap pasangan (ulasan, temuan) dari jalur mana pun (discovery, membership, atau
analyser aturan) dinilai di sini sebelum dihitung.

Rating sengaja tidak dipakai: teks yang sama mendapat label yang sama di 1★ dan 5★.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import lexicon

SUPPORTS, CONTRADICTS, UNRELATED, UNCERTAIN = "supports", "contradicts", "unrelated", "uncertain"


@dataclass(frozen=True)
class Verdict:
    label: str
    reason: str = ""
    clause: str = ""  # klausa asli yang paling mewakili label ini (verbatim dari ulasan)


def finding_scope(finding: dict) -> tuple[set[str], set[str]]:
    groups = lexicon.attribute_groups(finding.get("attribute", ""), finding.get("attribute_local", ""))
    extra = set() if groups else lexicon.attribute_terms(finding.get("attribute", ""),
                                                         finding.get("attribute_local", ""))
    return groups, extra


def judge(text: str, finding: dict, rating: int | None = None) -> Verdict:  # noqa: ARG001 - rating hanya metadata
    groups, extra = finding_scope(finding)
    parts = lexicon.clauses(text)
    wrong_item = lexicon.is_wrong_item(text)

    if groups == {"wrong_item"}:
        if wrong_item:
            clause = next((c.text for c in parts if lexicon.wrong_item_clause(c)), text)
            return Verdict(SUPPORTS, "", clause)
        return Verdict(UNRELATED, "not_a_wrong_item_report")

    support, contra, other_complaint, loose_complaint, neutral_mention = [], [], [], [], []
    for clause in parts:
        if wrong_item and lexicon.wrong_item_clause(clause):
            continue
        about = lexicon.mentions(clause.tokens, groups, extra)
        tone = lexicon.polarity(clause.tokens)
        if about and tone == "complaint":
            support.append(clause)
        elif about and tone == "praise":
            contra.append(clause)
        elif about:
            neutral_mention.append(clause)
        elif tone == "complaint":
            (other_complaint if lexicon.groups_in(clause.tokens) else loose_complaint).append(clause)

    operational = bool(groups & lexicon.OPERATIONAL_GROUPS)
    if wrong_item and not operational:
        # Varian lain yang datang adalah masalah operasional, bukan bukti tabel ukuran salah.
        if support:
            return Verdict(UNCERTAIN, "also_reports_wrong_variant", support[0].text)
        return Verdict(UNRELATED, "wrong_item_routes_to_operations")
    if support and contra:
        return Verdict(UNCERTAIN, "labelled_both_ways", support[0].text)
    if support:
        return Verdict(SUPPORTS, "", support[0].text)
    if contra:
        return Verdict(CONTRADICTS, "", contra[0].text)
    if other_complaint:
        return Verdict(UNRELATED, "complaint_not_about_this_attribute", other_complaint[0].text)
    if loose_complaint:
        return Verdict(UNCERTAIN, "complaint_without_attribute", loose_complaint[0].text)
    if neutral_mention:
        return Verdict(UNCERTAIN, "mentions_attribute_without_complaint", neutral_mention[0].text)
    return Verdict(UNRELATED, "not_about_this_attribute")
