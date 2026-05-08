from app.shared.permissions import has_scope


def test_has_scope_supports_exact_and_wildcards():
    assert has_scope(["pix.create"], "pix.create") is True
    assert has_scope(["pix.*"], "pix.charges.create") is True
    assert has_scope(["*"], "pix.webhook.receive") is True
    assert has_scope(["billing.read"], "pix.read") is False
