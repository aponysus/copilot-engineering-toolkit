"""Check synthetic ground truth without running an AI client."""

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType
from xml.etree import ElementTree

import pytest

FIXTURES = Path(__file__).parents[1] / "evals/fixtures"


def load_fixture(case: str, filename: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(case, FIXTURES / case / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retry_after_lost_response_duplicates_committed_job() -> None:
    module = load_fixture("retry_dispatch", "dispatch.py")
    queue = module.Queue()
    assert module.dispatch(queue, "job-1") == 2
    assert queue.jobs == ["job-1", "job-1"]


def test_dispatch_without_response_loss_commits_once() -> None:
    module = load_fixture("retry_dispatch", "dispatch.py")
    queue = module.Queue()
    queue.lose_next_response = False
    assert module.dispatch(queue, "job-1") == 1
    assert queue.jobs == ["job-1"]


@pytest.mark.parametrize("consumer", ["dashboard", "export_row"])
@pytest.mark.parametrize(
    ("payload", "failure"),
    [('{"item_count": 2}', KeyError), ('{"count": null}', TypeError)],
)
def test_api_changes_break_each_visible_consumer(
    consumer: str, payload: str, failure: type[Exception]
) -> None:
    module = load_fixture("api_consumers", "service.py")
    with pytest.raises(failure):
        getattr(module, consumer)(payload)


def test_configured_export_path_and_existing_wire_contract() -> None:
    module = load_fixture("api_consumers", "service.py")
    settings = json.loads((FIXTURES / "api_consumers/settings.json").read_text())
    assert module.response(2) == '{"count": 2}'
    assert module.destinations(module.response(2), settings["export_enabled"]) == [
        "3 including the pending item"
    ]
    assert module.destinations(module.response(2), True) == [
        "3 including the pending item",
        "items,2",
    ]


def test_reporting_fixture_demonstrates_end_boundary_contract_violation() -> None:
    module = load_fixture("period_boundary", "totals.py")
    events = [(10, 100), (20, 250)]
    # The maintained fixture intentionally has a bad oracle and implementation.
    assert module.period_total(events, 10, 20) == 350
    contract_total = sum(amount for timestamp, amount in events if 10 <= timestamp < 20)
    assert contract_total == 100
    adjacent = module.period_total(events, 10, 20) + module.period_total(events, 20, 30)
    assert adjacent == 600  # The shared-boundary event is counted twice.
    assert module.period_total(events, 10, 30) == 350


def test_onboarding_solution_references_resolve_to_distinct_frameworks() -> None:
    root = FIXTURES / "dotnet_onboarding"
    frameworks = {}
    for solution in root.glob("*.sln"):
        projects = re.findall(r'"([^"\n]+\.csproj)"', solution.read_text())
        assert projects
        frameworks[solution.stem] = []
        for reference in projects:
            project = root.joinpath(*reference.split("\\"))
            tree = ElementTree.parse(project)
            frameworks[solution.stem].append(tree.findtext(".//TargetFramework"))
            for dependency in tree.findall(".//ProjectReference"):
                assert (project.parent / dependency.attrib["Include"]).is_file()
    assert frameworks == {"Legacy": ["net48", "net48"], "Modern": ["net8.0"]}
