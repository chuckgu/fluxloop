import json

from fluxloop_cli.conversation_supervisor import format_transcript


def test_format_transcript_handles_dict_content() -> None:
    turns = [
        {
            "role": "assistant",
            "content": {"message": "Hello", "meta": {"foo": "bar"}},
        }
    ]

    rendered = format_transcript(turns)

    assert "Assistant" in rendered
    assert "message" in rendered
    assert "foo" in rendered


def test_format_transcript_handles_tool_call_arguments() -> None:
    turns = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "name": "lookup_policy",
                    "arguments": {"query": "test question"},
                }
            ],
        }
    ]

    rendered = format_transcript(turns)

    assert "lookup_policy" in rendered
    assert "test question" in rendered

