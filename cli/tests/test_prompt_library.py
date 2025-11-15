from fluxloop_cli.evaluation.prompts import (
    PROMPT_BUNDLES,
    get_prompt_bundle,
    list_prompt_bundles,
)


def test_prompt_bundle_registry_contains_expected_keys() -> None:
    keys = sorted(bundle.key for bundle in list_prompt_bundles())
    assert keys == [
        "information_completeness",
        "intent_recognition",
        "response_clarity",
        "response_consistency",
    ]


def test_prompt_bundle_uses_standard_header() -> None:
    bundle = get_prompt_bundle("intent_recognition")
    text = bundle.with_header()
    assert text.startswith(f"# {bundle.title}")
    assert "Score:" in text and "Reason:" in text
    assert "1 (very poor)" in text


def test_prompt_bundle_sample_response() -> None:
    for bundle in PROMPT_BUNDLES.values():
        assert bundle.sample_response.startswith("Score: ")
        assert "Reason:" in bundle.sample_response
