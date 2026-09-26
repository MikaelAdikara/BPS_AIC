"""Rescoring must preserve human work and never attach labels to changed output."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eval"))
import scoring


def test_rescore_preserves_rater_labels_only_for_same_output(tmp_path):
    case = {"id": "t", "status": "development", "category": [], "forbidden_before": [], "gold": {
        "route": "none", "attribute_words": [], "supports": [], "fact_needed": False}}
    row = {"case_id": "t", "system": "B1", "phase": "before", "status": "ok",
           "text": "No recurring problem found."}
    rows = {("t", "before", "B1"): row}
    scoring.write_all([case], rows, tmp_path)
    path = tmp_path / "labels.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        labels = list(csv.DictReader(fh))
    labels[0].update(rater="human-a", notes="checked", unsafe_claim_0_1="0")
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(labels[0]))
        writer.writeheader()
        writer.writerows(labels)
    scoring.write_all([case], rows, tmp_path)
    with path.open(encoding="utf-8", newline="") as fh:
        assert list(csv.DictReader(fh))[0]["notes"] == "checked"
    row["text"] = "Changed answer requiring new judgement."
    scoring.write_all([case], rows, tmp_path)
    with path.open(encoding="utf-8", newline="") as fh:
        assert list(csv.DictReader(fh))[0]["rater"] == ""
    assert (tmp_path / "labels.previous.csv").exists()
