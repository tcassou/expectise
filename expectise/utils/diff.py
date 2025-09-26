import difflib
import textwrap
from typing import Any

# Iterable types represented recursively, one element per line
ITERABLES = {
    set: {"l": "{", "r": "}"},
    list: {"l": "[", "r": "]"},
    dict: {"l": "{", "r": "}"},
    tuple: {"l": "(", "r": ")"},
}
# Diff colors: green for additions, red for deletions, default white
COLORS = {
    "+": "\033[92m",
    "-": "\033[91m",
    ".": "\033[0m",
}


class Diff:
    @staticmethod
    def repr(obj: Any, indent: int = 0) -> str:
        """Multiline representation of input object `obj`, recursively processing nested objects."""
        t = type(obj)
        if t not in ITERABLES:
            # Using the default representation of non iterable objects
            return Diff.indent(obj.__repr__(), indent)

        if t == dict:
            # "key: value," format for each line
            content = [f"{Diff.repr(k, indent + 2)}: {Diff.repr(v)}," for k, v in obj.items()]
        else:
            # "value," format for each line
            content = [f"{Diff.repr(o, indent + 2)}," for o in obj]

        return "\n".join([Diff.indent(ITERABLES[t]["l"], indent)] + content + [Diff.indent(ITERABLES[t]["r"], indent)])

    @staticmethod
    def indent(s: str, k: int) -> str:
        """Indents the input string `s` with `k` spaces."""
        return textwrap.indent(s, " " * k)

    @staticmethod
    def print(left: Any, right: Any) -> str:
        """Build a git-style text diff of `left` and `right` input objects."""
        lines_diff = difflib.ndiff(Diff.repr(left).split("\n"), Diff.repr(right).split("\n"))
        return "\n".join(
            [COLORS.get(line[0], COLORS["."]) + line + COLORS["."] for line in lines_diff if not line.startswith("?")]
        )
