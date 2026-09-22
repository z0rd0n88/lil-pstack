#!/usr/bin/env python3
"""Remove sentence dashes from markdown, branching on line type.

Implements the substitution table in the unslop skill's rule 13. Em dashes are
always converted; en dashes only when they sit between spaces (a spaced en dash
is a sentence dash, an unspaced one is a range or a compound). Hyphens, fenced
code blocks, indented code blocks and inline backtick spans are left alone.

Usage: undash.py [--check] [--diff] FILE...
       undash.py --self-test
       undash.py --help
"""

import contextlib
import difflib
import io
import os
import re
import sys
import tempfile

FENCE = re.compile(r"^\s*(```|~~~)")
INDENT = re.compile(r"^(?:\t| {4})")
CODE = re.compile(r"`[^`]*`")
SPACED_EN = re.compile(r"(?<=\s)–(?=\s)")
DASH = re.compile(r"\s*—\s*")
# A bold label only counts when the line opens with it, optionally after a
# bullet or a numbered marker. Bold in mid sentence is not a label.
BOLD_LEAD = re.compile(r"^\s*(?:[-*]\s+|\d+[.)]\s+)?\*\*[^*].*\*\*$")

USAGE = (
    "usage: undash.py [--check] [--diff] FILE...\n"
    "       undash.py --self-test\n"
    "       undash.py --help"
)


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


def _cap(text):
    """Upper-case the first letter, stepping over markup like *, _ or [."""
    for i, ch in enumerate(text):
        if ch.isalpha():
            return text[:i] + ch.upper() + text[i + 1 :]
    return text


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
        if not head.strip():
            # The dash opens the line. Drop it and start on the next word.
            line = re.match(r"\s*", line).group(0) + _cap(tail)
        elif not tail.strip():
            # The dash trails the line. Drop it and the space before it.
            line = head
        else:
            clause = DASH.split(tail, 1)[0]
            if BOLD_LEAD.match(head) or len(clause.split()) >= 7:
                line = head + ". " + _cap(tail)
            else:
                line = head + ", " + tail


def _fix_line(line):
    line, spans = _protect(line)
    line = SPACED_EN.sub("—", line)
    line = re.sub(r"(\d)\s*—\s*(\d)", r"\1 to \2", line)
    stripped = line.lstrip()
    if stripped.startswith("#"):
        # One colon per heading. A second dash reads as a comma.
        line = DASH.sub(": ", line, count=1)
        line = DASH.sub(", ", line)
    elif stripped.startswith("|"):
        line = _fix_row(line)
    else:
        line = _fix_prose(line)
    return _restore(line, spans)


def _lines(text):
    """Yield (line, in_code) for every line of text."""
    marker = None
    prev = None  # the line immediately before this one
    prev_code = False  # whether the last non-blank line was indented code
    for line in text.split("\n"):
        fence = FENCE.match(line)
        if marker:
            # Only the marker that opened the fence can close it.
            if fence and fence.group(1)[0] == marker[0]:
                marker = None
            code = True
        elif fence:
            marker = fence.group(1)
            code = True
        else:
            code = bool(INDENT.match(line)) and (
                prev is None or not prev.strip() or prev_code
            )
        yield line, code
        if line.strip():
            prev_code = code and not fence and marker is None
        prev = line


def convert(text):
    return "\n".join(l if code else _fix_line(l) for l, code in _lines(text))


def live_dashes(text):
    """Count dashes this script would act on: outside code, em or spaced en."""
    n = 0
    for line, code in _lines(text):
        if not code:
            bare = CODE.sub("", line)
            n += bare.count("—") + len(SPACED_EN.findall(bare))
    return n


def _parse(argv):
    """Return (mode, files). Mode is write, check, diff, self-test, help or bad."""
    mode, files = "write", []
    for arg in argv:
        if arg in ("-h", "--help"):
            return "help", []
        if arg == "--self-test":
            mode = "self-test"
        elif arg == "--check":
            mode = "check"
        elif arg == "--diff":
            mode = "diff"
        elif arg.startswith("--"):
            return "bad", [arg]
        else:
            files.append(arg)
    return mode, files


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

    # 1: a ``` line inside a ~~~ block does not close it.
    assert (
        convert("~~~\na — b\n```\nc — d\n~~~\ne — f.")
        == "~~~\na — b\n```\nc — d\n~~~\ne, f."
    )
    # 5: a line that opens with a dash loses the dash, not the first word.
    assert _fix_line("— then it ran.") == "Then it ran."
    # 6: an indented code block is left alone.
    assert convert("text\n\n    x — y\n    z — w") == "text\n\n    x — y\n    z — w"
    # 6: wrapped list text is prose, not code.
    assert convert("- item\n    more — text") == "- item\n    more, text"
    # 7: bold in mid sentence is not a label, so no full stop.
    assert (
        _fix_line("This is **important** — but not always.")
        == "This is **important**, but not always."
    )
    # 8: a trailing dash leaves no comma behind.
    assert _fix_line("Stop here —") == "Stop here"
    # 10: the second dash in a heading is a comma, not a second colon.
    assert _fix_line("## A — b — c") == "## A: b, c"
    # 11: capitalize past leading markup.
    assert (
        _fix_line("It works — *the parser reads every line before it writes*.")
        == "It works. *The parser reads every line before it writes*."
    )
    # 3: an unknown flag is an error, and -h asks for usage.
    assert _parse(["--dif", "x.md"])[0] == "bad"
    assert _parse(["-h"])[0] == "help"

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "crlf.md")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("It works — mostly.\r\nnext line\r\n")
        with contextlib.redirect_stdout(io.StringIO()):
            main([path])
        with open(path, encoding="utf-8", newline="") as f:
            got = f.read()
        # 2: a CRLF file stays CRLF.
        assert got == "It works, mostly.\r\nnext line\r\n", repr(got)
        # 4: a missing file is skipped, the rest of the batch still runs.
        with contextlib.redirect_stdout(io.StringIO()):
            with contextlib.redirect_stderr(io.StringIO()) as err:
                rc = main([os.path.join(d, "gone.md"), path])
        assert rc == 3, rc
        assert "gone.md: skipped" in err.getvalue(), err.getvalue()
    print("ok")


def main(argv):
    mode, files = _parse(argv)
    if mode == "help":
        print(USAGE)
        return 0
    if mode == "bad":
        print("undash.py: unknown option %s" % files[0], file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    if mode == "self-test":
        self_test()
        return 0
    if not files:
        print(USAGE, file=sys.stderr)
        return 2

    failed = False
    skipped = False
    for path in files:
        try:
            with open(path, encoding="utf-8", newline="") as f:
                raw = f.read()
        except (OSError, UnicodeDecodeError) as e:
            print("%s: skipped (%s)" % (path, e), file=sys.stderr)
            skipped = True
            continue
        newline = "\r\n" if "\r\n" in raw else "\n"
        before = raw.replace("\r\n", "\n")
        after = convert(before)
        out = after.replace("\n", newline) if newline != "\n" else after
        if mode == "check":
            n = live_dashes(before)
            print("%s: %d dashes" % (path, n))
            failed = failed or n > 0
        elif mode == "diff":
            sys.stdout.writelines(
                difflib.unified_diff(
                    raw.splitlines(True),
                    out.splitlines(True),
                    path,
                    path + " (undashed)",
                )
            )
        else:
            if out != raw:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(out)
            print(
                "%s: %d dashes -> %d" % (path, live_dashes(before), live_dashes(after))
            )
    if skipped:
        return 3
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
