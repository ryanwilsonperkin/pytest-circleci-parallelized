def test_with_circleci_parallelize(testdir):
    testdir.makepyfile(
        test_fast_slow_classes="""
import time
import unittest

class SlowTestCase(unittest.TestCase):
    def test_something(self):
        time.sleep(5)
        assert True

class FastTestCase1(unittest.TestCase):
    def test_something(self):
        time.sleep(1)
        assert True

class FastTestCase2(unittest.TestCase):
    def test_something(self):
        time.sleep(1)
        """
    )

    result = testdir.runpytest(
        "-v",
        "--circleci-parallelize",
        "--junitxml=/tmp/integration-test-reports/junit.xml",
    )
    if "running 1 items" in result.stdout.str():
        # If the node only ran one item it should be the slow one
        result.stdout.fnmatch_lines(["*SlowTestCase::test_something PASSED*"])
    elif "running 2 items" in result.stdout.str():
        # If the node ran two items it should be the fast ones
        result.stdout.fnmatch_lines_random(
            [
                "*FastTestCase1::test_something PASSED*",
                "*FastTestCase2::test_something PASSED*",
            ]
        )
    else:
        assert False, "Test splitting should cause only 1 or 2 items to be run."

    assert result.ret == 0

def test_with_fewer_tests_than_runners(testdir):
    testdir.makepyfile(
        test_fast_slow_classes="""
import time
import unittest

class Test1(unittest.TestCase):
    def test_something(self):
        assert True

class Test2(unittest.TestCase):
    def test_something(self):
        assert True

        """
    )

    result = testdir.runpytest(
        "-v",
        "--circleci-parallelize",
        "--junitxml=/tmp/integration-test-reports/junit.xml",
    )
    result.stdout.re_match_lines(["Test[12]::test_something PASSED"])
    assert result.ret == 0
