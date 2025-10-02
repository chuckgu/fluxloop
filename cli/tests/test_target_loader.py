"""Tests for the TargetLoader utility."""

import sys
from types import ModuleType

import pytest

from fluxloop.schemas import RunnerConfig
from fluxloop_cli.target_loader import TargetLoader


@pytest.fixture
def temporary_module(monkeypatch):
    module = ModuleType("test_module")

    class SampleAgent:
        def __init__(self):
            self.counter = 0

        def run(self, value: str) -> str:
            self.counter += 1
            return f"processed:{value}:{self.counter}"

    def standalone(value: str) -> str:
        return f"standalone:{value}"

    module.SampleAgent = SampleAgent
    module.standalone = standalone

    monkeypatch.setitem(sys.modules, "test_module", module)

    yield module

    monkeypatch.delitem(sys.modules, "test_module", raising=False)


def test_load_function_target(temporary_module):
    config = RunnerConfig(
        module_path="ignored",
        function_name="ignored",
        target="test_module:standalone",
    )

    loader = TargetLoader(config)
    func = loader.load()

    assert func("value") == "standalone:value"


def test_load_class_method_target(temporary_module):
    config = RunnerConfig(
        module_path="ignored",
        function_name="ignored",
        target="test_module:SampleAgent.run",
    )

    loader = TargetLoader(config)
    method = loader.load()

    assert method("value") == "processed:value:1"
    assert method("again") == "processed:again:2"


def test_invalid_target_format():
    config = RunnerConfig(
        module_path="ignored",
        function_name="ignored",
        target="invalidformat",
    )

    loader = TargetLoader(config)

    with pytest.raises(ValueError, match="Invalid runner.target format"):
        loader.load()


def test_missing_class_raises():
    config = RunnerConfig(
        module_path="ignored",
        function_name="ignored",
        target="test_module:Missing.run",
    )

    loader = TargetLoader(config)

    with pytest.raises(ValueError, match="Failed to import module"):
        loader.load()


