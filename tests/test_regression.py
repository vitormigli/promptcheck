from promptcheck.regression import compare_to_baseline
from promptcheck.runner import TestResult


def _result(id_, passed):
    return TestResult(id=id_, passed=passed, response_text="x")


def test_detects_regression():
    baseline = {"a": True, "b": True}
    current = [_result("a", True), _result("b", False)]
    report = compare_to_baseline(current, baseline)
    assert report.regressions == ["b"]
    assert report.has_regressions


def test_no_regression_when_all_still_passing():
    baseline = {"a": True}
    current = [_result("a", True)]
    report = compare_to_baseline(current, baseline)
    assert not report.has_regressions


def test_already_failing_test_is_not_a_new_regression():
    baseline = {"a": False}
    current = [_result("a", False)]
    report = compare_to_baseline(current, baseline)
    assert report.regressions == []
    assert report.unchanged_fail == ["a"]


def test_fixed_test_detected():
    baseline = {"a": False}
    current = [_result("a", True)]
    report = compare_to_baseline(current, baseline)
    assert report.fixed == ["a"]


def test_new_test_not_counted_as_regression():
    baseline = {}
    current = [_result("brand_new", False)]
    report = compare_to_baseline(current, baseline)
    assert report.new_tests == ["brand_new"]
    assert not report.has_regressions
