
import difflib
import re


# Extract dynamic variables
def extract_variables(prompt_text: str) -> list[str]:

    pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"

    return sorted(set(re.findall(pattern, prompt_text)))


# Validate dynamic variables
def validate_variables(prompt_text: str) -> bool:

    valid_pattern = r"\{[a-zA-Z_][a-zA-Z0-9_]*\}"

    remaining_text = re.sub(
        valid_pattern,
        "",
        prompt_text
    )

    if "{" in remaining_text or "}" in remaining_text:
        return False

    return True


# Compare two prompt versions
def compute_text_diff(text1: str, text2: str) -> str:

    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile="Version A",
        tofile="Version B"
    )

    return "".join(diff)
