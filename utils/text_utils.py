import re


def strip_links(s: str) -> str:
    return re.sub(
        r"http\S+",
        "link",
        s,
        flags=re.MULTILINE,
    )
