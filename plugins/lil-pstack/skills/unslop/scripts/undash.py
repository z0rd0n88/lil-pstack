#!/usr/bin/env python3
"""Remove sentence dashes from markdown, branching on line type.

Implements the substitution table in the unslop skill's rule 13. Em dashes are
always converted; en dashes only when they sit between spaces (a spaced en dash
is a sentence dash, an unspaced one is a range or a compound). Hyphens, fenced
code blocks and inline backtick spans are left alone.

Usage: undash.py [--check] [--diff] FILE...
       undash.py --self-test
"""

import difflib
import re
import sys

FENCE = re.compile(r"^\s*(```|~~~)")
CODE = re.compile(r"`[^`]*`")
SPACED_EN = re.compile(r"(?<=\s)–(?=\s)")
DASH = re.compile(r"\s*—\s*")


def _protect(line):
    """Swap inline code spans for placeholders so substitutions skip them."""
    spans = []

    def take(m):
        spans.append(m.group(0))
        return "\x00%d\x00" % (len(spans) - 1)

    return CODE.sub(take, line), spans


def _restore(line, spans):
    for i, span in enumerate(spans):
        line = line.replace("\x00%d\x00" % i, span)
    return line


def _fix_row(line):
    cells = []
    for cell in line.split("|"):
        if cell.strip() == "—":
            cell = cell.replace("—", "none")
        else:
            cell = re.sub(r"^(\s*)—\s*", r"\1", cell)
        cells.append(cell)
    return DASH.sub(", ", "|".join(cells))


def _fix_prose(line):
    while True:
        m = DASH.search(line)
        if not m:
            return line
        head, tail = line[: m.start()].rstrip(), line[m.end() :]
        clause = DASH.split(tail, 1)[0]
        if head.endswith("**") or len(clause.split()) >= 7:
            line = head + ". " + tail[:1].upper() + tail[1:]
        else:
            line = head + ", " + tail


def _fix_line(line):
    line, spans = _protect(line)
    line = SPACED_EN.sub("—", line)
    line = re.sub(r"(\d)\s*—\s*(\d)", r"\1 to \2", line)
    stripped = line.lstrip()
    if stripped.startswith("#"):
        line = DASH.sub(": ", line)
    elif stripped.startswith("|"):
        line = _fix_row(line)
    else:
        line = _fix_prose(line)
    return _restore(line, spans)


def _lines(text):
    """Yield (line, in_fence) for every line of text."""
    fenced = False
    for line in text.split("\n"):
        if FENCE.match(line):
            fenced = not fenced
            yield line, True
        else:
            yield line, fenced


def convert(text):
    return "\n".join(l if fenced else _fix_line(l) for l, fenced in _lines(text))


def live_dashes(text):
    """Count dashes this script would act on: outside code, em or spaced en."""
    n = 0
    for line, fenced in _lines(text):
        if not fenced:
            bare = CODE.sub("", line)
            n += bare.count("—") + len(SPACED_EN.findall(bare))
    return n


def self_test():
    assert _fix_line("## Stage 1 — Name") == "## Stage 1: Name"
    assert _fix_line("| a | — | b |") == "| a | none | b |"
    assert _fix_line("| a | — yes | b |") == "| a | yes | b |"
    assert _fix_line("| a | one — two |") == "| a | one, two |"
    assert _fix_line("Ran 3 — 5 times.") == "Ran 3 to 5 times."
    assert (
        _fix_line("It works — the parser reads every line before it writes.")
        == "It works. The parser reads every line before it writes."
    )
    assert _fix_line("It works — mostly.") == "It works, mostly."
    assert (
        _fix_line("**Schema** — tables live in one file.")
        == "**Schema**. Tables live in one file."
    )
    assert _fix_line("Set a – b apart.") == "Set a, b apart."
    assert _fix_line("Keep `a — b` as is.") == "Keep `a — b` as is."
    assert convert("```\nx — y\n```\na — b.") == "```\nx — y\n```\na, b."
    assert live_dashes("```\nx — y\n```\nsee `a — b`") == 0
    print("ok")


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    files = [a for a in argv if not a.startswith("--")]
    if "--self-test" in flags:
        self_test()
        return 0
    if not files:
        print(__doc__.strip().split("\n\n")[-1], file=sys.stderr)
        return 2

    failed = False
    for path in files:
        with open(path, encoding="utf-8") as f:
            before = f.read()
        after = convert(before)
        if "--check" in flags:
            n = live_dashes(before)
            print("%s: %d dashes" % (path, n))
            failed = failed or n > 0
        elif "--diff" in flags:
            sys.stdout.writelines(
                difflib.unified_diff(
                    before.splitlines(True),
                    after.splitlines(True),
                    path,
                    path + " (undashed)",
                )
            )
        else:
            if after != before:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(after)
            print(
                "%s: %d dashes -> %d" % (path, live_dashes(before), live_dashes(after))
            )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
