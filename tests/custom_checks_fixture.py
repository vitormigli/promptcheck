"""A sample custom-check module, referenced by test_assertions.py's
`custom` assertion test via "tests.custom_checks_fixture:is_uppercase"."""


def is_uppercase(text: str, response) -> bool:
    return text == text.upper()
