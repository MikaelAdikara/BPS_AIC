from app.deciqo.engine import membership


def test_membership_keeps_review_tail_and_bounds_batch_size(monkeypatch):
    reviews = [{"id": f"r{i}", "text": "Bagus. " * 120 + "Tapi barang rusak.", "rating": 4}
               for i in range(151)]
    inputs = []
    monkeypatch.setattr(membership.llm, "call_json", lambda **kwargs:
        (inputs.append(kwargs["user"]) or {"labels": []}, {}))
    membership.run([{"attribute": "quality"}], reviews)
    assert len(inputs) >= 4
    for review in reviews:
        assert sum(f"id={review['id']} " in text for text in inputs) == 1
        assert any(review["text"] in text for text in inputs)
