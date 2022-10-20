# pytest-circleci-parallelized

[![PyPI version](https://img.shields.io/pypi/v/pytest-circleci-parallelized.svg)](https://pypi.org/project/pytest-circleci-parallelized) [![Python versions](https://img.shields.io/pypi/pyversions/pytest-circleci-parallelized.svg)](https://pypi.org/project/pytest-circleci-parallelized) [![CircleCI build status](https://circleci.com/gh/ryanwilsonperkin/pytest-circleci-parallelized.svg?style=svg)](https://circleci.com/gh/ryanwilsonperkin/pytest-circleci-parallelized)

Parallelize pytest across CircleCI workers.

---

## Features

Leverage the builtin parallelism of CircleCI to run your test suites. Call `pytest` with the `--circleci-parallelize` flag to automatically split tests amongst nodes using the `circleci tests split` utility.

Read more about CircleCI test splitting [here][circleci-test-splitting].

```yaml
# .circleci/config.yml
version: 2
jobs:
  test:
    docker:
      - image: circleci/python:3
    parallelism: 10
    steps:
      - checkout
      - run: pytest --circleci-parallelize
workflows:
  version: 2
  test:
    jobs:
      - test
```

## Installation

You can install "pytest-circleci-parallelized" via pip from [PyPI][pypi].

```sh
pip install pytest-circleci-parallelized
```

## Contributing

Contributors welcome! Tests can be run with [`pytest`][pytest]

## License

Distributed under the terms of the [MIT](/LICENSE) license, `pytest-circleci-parallelized` is free and open source software.

## Issues

If you encounter any problems, please [file an issue](new-issue) along with a detailed description.

[pypi]: https://pypi.org/project/pytest-circleci-parallelized/
[new-issue]: https://github.com/ryanwilsonperkin/pytest-circleci-parallelized/issues/new
[circleci-test-splitting]: https://circleci.com/docs/2.0/parallelism-faster-jobs/
