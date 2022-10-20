# -*- coding: utf-8 -*-
import collections
import subprocess

import pytest


def pytest_addoption(parser):
    group = parser.getgroup("circleci-parallelized")
    group.addoption(
        "--circleci-parallelize",
        dest="circleci_parallelize",
        action="store_true",
        default=False,
        help="Enable parallelization across CircleCI containers.",
    )


def get_verbosity(config):
    return config.option.verbose


def circleci_parallelized_enabled(config):
    return config.getoption("circleci_parallelize")


def pytest_report_collectionfinish(config, startdir, items):
    if circleci_parallelized_enabled(config):
        verbosity = get_verbosity(config)
        if verbosity == 0:
            return "running {} items due to CircleCI parallelism".format(len(items))
        elif verbosity > 0:
            return "running {} items due to CircleCI parallelism: {}".format(
                len(items), ", ".join(map(get_class_name, items))
            )
    else:
        return ""


def get_class_name(item):
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


def filter_tests_with_circleci(test_list):
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


@pytest.hookimpl(hookwrapper=True)
def pytest_cmdline_main(config):
    outcome = yield config
    exit_code = outcome.get_result()

    # Exit Code 5 indicates no tests were collected
    # https://docs.pytest.org/en/7.1.x/reference/exit-codes.html
    # If there are more workers than tests, this can cause "No Tests" error
    # This is fine, and we cast it to an OK exit code
    if circleci_parallelized_enabled(config) and exit_code == 5:
        outcome.force_result(0)


def pytest_collection_modifyitems(session, config, items):
    if not circleci_parallelized_enabled(config):
        return

    class_mapping = collections.defaultdict(list)
    for item in items:
        class_name = get_class_name(item)
        class_mapping[class_name].append(item)

    filtered_tests = filter_tests_with_circleci(class_mapping.keys())

    new_items = []
    for name in filtered_tests:
        new_items.extend(class_mapping[name])

    items[:] = new_items
