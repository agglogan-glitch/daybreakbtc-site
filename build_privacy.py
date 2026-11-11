#!/usr/bin/env python3
"""Make site/privacy/index.html from docs/privacy-policy.md (Python 3 standard library only).

Run from the repo root after editing the policy:  python3 site/build_privacy.py
Handles the small Markdown subset the policy uses: #/## headings, paragraphs, "- " lists,
> quotes, **bold**, *italic*, [links](url) and <!-- comments --> (comments are dropped).
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "privacy-policy.md"
OUT = ROOT / "site" / "privacy" / "index.html"


def inline(text: str) -> str:
    t = html.escape(text, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", lambda m: f'<a href="{html.escape(m.group(2))}" rel="noopener noreferrer">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def convert(md: str) -> tuple[str, str]:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out: list[str] = []
    title = "Privacy Policy"
    para: list[str] = []
    items: list[str] = []
    quote: list[str] = []

    def flush():
        nonlocal para, items, quote
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
        if items:
            out.append("<ul>\n" + "\n".join(f"  <li>{inline(i)}</li>" for i in items) + "\n</ul>")
            items = []
        if quote:
            body = "<br>\n".join(inline(q) for q in quote)
            out.append(f'<aside class="draft" role="note">\n<!-- REMOVE this draft note from the public page once a lawyer has reviewed the policy. -->\n<p>{body}</p>\n</aside>')
            quote = []

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if line.startswith("# "):
            flush()
            title = line[2:].strip()
            out.append(f"<h1>{inline(title)}</h1>")
        elif line.startswith("## "):
            flush()
            text = line[3:].strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h2 id="{anchor}">{inline(text)}</h2>')
        elif line.startswith("- "):
            if para:
                flush()
            items.append(line[2:].strip())
        elif line.startswith(">"):
            if para or items:
                flush()
            quote.append(line.lstrip("> ").strip())
        elif items and raw.startswith("  "):
            items[-1] += " " + line.strip()
        else:
            if items:
                flush()
            para.append(line.strip())
    flush()
    return title, "\n".join(out)


def main() -> None:
    title, body = convert(SRC.read_text(encoding="utf-8"))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="How the Daybreak BTC app handles your information, in plain words.">
<link rel="icon" href="../favicon.ico" sizes="any">
<link rel="icon" href="../logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="stylesheet" href="../styles.css">
</head>
<body>
<!-- Generated from docs/privacy-policy.md by site/build_privacy.py. Edit the Markdown, then re-run. -->
<header class="bar"><a class="brand" href="../"><img src="../logo.svg" alt="" width="32" height="32"> Daybreak BTC</a></header>
<main class="doc">
{body}
</main>
<footer class="foot"><a href="../">Home</a> · <a href="./">Privacy</a></footer>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
