# -*- coding: utf-8 -*-
import collections
import subprocess
from typing import DefaultDict, Iterable, List, Optional, Sequence, Union

import pytest
from py.path import local as LocalPath


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("circleci-parallelized")
    group.addoption(
        "--circleci-parallelize",
        dest="circleci_parallelize",
        action="store_true",
        default=False,
        help="Enable parallelization across CircleCI containers.",
    )


def get_verbosity(config: pytest.Config) -> int:
    return int(config.option.verbose)


def circleci_parallelized_enabled(config: pytest.Config) -> bool:
    return bool(config.getoption("circleci_parallelize"))


def pytest_report_collectionfinish(
    config: pytest.Config, startdir: LocalPath, items: Sequence[pytest.Item]
) -> Union[str, List[str]]:
    if circleci_parallelized_enabled(config):
        verbosity = get_verbosity(config)
        if verbosity == 0:
            return "running {} items due to CircleCI parallelism".format(len(items))
        elif verbosity > 0:
            class_names = map(get_class_name, items)
            not_null_class_names = (
                class_name for class_name in class_names if class_name is not None
            )

            return "running {} items due to CircleCI parallelism: {}".format(
                len(items), ", ".join(not_null_class_names)
            )

    return ""


def get_class_name(item: pytest.Item) -> Optional[str]:
    class_name, module_name = None, None
    for parent in reversed(item.listchain()):
        if isinstance(parent, pytest.Class):
            class_name = parent.name
        elif isinstance(parent, pytest.Module):
            module_name = parent.module.__name__
            break

    if class_name:
        return "{}.{}".format(module_name, class_name)
    else:
        return module_name


def filter_tests_with_circleci(test_list: Iterable) -> List:
    circleci_input = "\n".join(test_list).encode("utf-8")
    p = subprocess.Popen(
        [
            "circleci",
            "tests",
            "split",
            "--split-by=timings",
            "--timings-type=classname",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    circleci_output, _ = p.communicate(circleci_input)
    return [
        line.strip() for line in circleci_output.decode("utf-8").strip().split("\n")
    ]


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: List[pytest.Item]
) -> None:
    if not circleci_parallelized_enabled(config):
        return

    class_mapping: DefaultDict[str, List[pytest.Item]] = collections.defaultdict(list)
    for item in items:
        class_name = get_class_name(item)
        if class_name is None:
            continue
        class_mapping[class_name].append(item)

    filtered_tests = filter_tests_with_circleci(class_mapping.keys())

    new_items = []
    for name in filtered_tests:
        new_items.extend(class_mapping[name])

    items[:] = new_items
