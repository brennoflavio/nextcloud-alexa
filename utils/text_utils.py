import re
import html2text


def strip_links(s: str) -> str:
    return re.sub(
        r"http\S+",
        "link",
        s,
        flags=re.MULTILINE,
    )


def strip_html(html_string: str) -> str:
    return html2text.html2text(html_string)
