from unittest import TestCase


def assert_log_contains_all(test_case: TestCase, log_text: str, fragments: list[str]) -> None:
    for fragment in fragments:
        test_case.assertIn(fragment, log_text)


def assert_log_contains_none(test_case: TestCase, log_text: str, fragments: list[str]) -> None:
    for fragment in fragments:
        test_case.assertNotIn(fragment, log_text)


def assert_live_line_log(
    test_case: TestCase,
    log_text: str,
    *,
    relative_path: str,
    final_line: int,
    origin_file: str,
    origin_line: int,
    revision_id: str,
    classification: str,
) -> None:
    fragment = (
        f"LiveLine {relative_path}:{final_line} aggregate "
        f"origin={origin_file}:{origin_line}@{revision_id} "
        f"classification={classification}"
    )
    test_case.assertIn(fragment, log_text)


def assert_transition_hint(test_case: TestCase, log_text: str, before: str, after: str) -> None:
    test_case.assertIn(f"best_effort_transition={before}->{after}", log_text)