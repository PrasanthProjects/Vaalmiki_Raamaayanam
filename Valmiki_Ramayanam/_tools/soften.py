"""Soft words for image and video prompts (2026-11-06).

AI image and video tools refuse prompts that name blood, wounds, gore, death or killing, even in a "no blood"
rule. Every prompt the Shorts and long-video kits print goes through soften(): blood becomes a deep red colour,
wounds become marks, death becomes the end, and the "no gore" rules become one positive line. The same RULES are
sent to the published pages, which apply them when they load (see rules_js()).
"""
import json
import re

CLEAN = "every struggle shown in a clean, dignified, family-friendly way"
# (pattern, replacement), applied in order, case-insensitive; a capital first letter is kept.
RULES = [
    # the standard rule lines
    (r"no blood, wounds, gore or graphic violence", CLEAN),
    (r",?\s*(?:and\s+)?(?:never any|no) blood or gore", ""),
    (r"\(no gore\)", "(shown gently)"),
    (r",\s*no gore\b", ""),
    (r"\bno gore,?\s*", ""),
    (r"(?:but not|rather than) gory", "yet gentle"),
    (r"never gory or ", "never "),
    (r"never gory", "always gentle"),
    (r"no close-up of the wounds", "no close-up"),
    (r"\(the wound not shown in close-up\)", "(shown gently from a distance)"),
    (r"\(shown as release, not wound\)", "(shown as release)"),
    (r"graphic violence", "harsh scenes"),
    # blood
    (r"blood suggested only", "only a touch of deep red colour"),
    (r"blood-guilt", "sin"),
    (r"bloodshot", "deep red"),
    (r"blood-red", "deep crimson"),
    (r"\bbloody\b", "red-stained"),
    (r"\bbleeding\b", "with streaks of deep red colour"),
    (r"\bbleeds?\b", "shows streaks of deep red colour"),
    (r"\bblood\b", "deep red colour"),
    # wounds and harm
    (r"\bwound with\b", "wrapped with"),
    (r"shares the same wound", "shares the same sorrow"),
    (r"fatally wounded", "gravely weakened"),
    (r"\bwounded\b", "weakened"),
    (r"\bwounds\b", "deep red marks"),
    (r"\bwound\b", "deep red mark"),
    (r"\binjur(?:ed|ies|y)\b", "hurt"),
    (r"\bscarred\b", "weathered"),
    (r"\bscars\b", "marks"),
    (r"\bmutilation\b", "humiliation"),
    (r"\bpierces\b", "passes through"),
    (r"\bpierced\b", "struck"),
    (r"\bpiercing\b", "sharp"),
    (r"\bpierce\b", "pass through"),
    (r"\bgory\b", "harsh"),
    (r"\bgore\b", "harshness"),
    (r"\bcarcass(?:es)?\b", "remains"),
    (r"\bcorpses?\b", "statue"),
    # death and killing
    (r"a dead man", "a doomed man"),
    (r"\bthe dead\b", "the departed"),
    (r"\bdead\b", "gone"),
    (r"\bdying\b", "fading"),
    (r"\bdies\b", "passes away"),
    (r"death scene", "final scene"),
    (r"figure of death", "figure of doom"),
    (r"\bdeathbed\b", "final bed"),
    (r"\bdeaths\b", "ends"),
    (r"\bdeath\b", "end"),
    (r"never killed", "never harmed"),
    (r"mother-slayer", "one who wrongs his mother"),
    (r"\bkill(?:ed|s)\b", "defeated"),
    (r"\bkilling\b", "defeating"),
    (r"\bkill\b", "defeat"),
    (r"\bslain\b", "defeated"),
    (r"\bslaying\b", "defeating"),
    (r"\bslayer\b", "victor"),
    (r"\bslay\b", "defeat"),
    (r"\bbehead(?:ed|s)?\b", "struck down"),
    (r"\bsever(?:ed|s)\b", "struck"),
]
_COMPILED = [(re.compile(p, re.I), r) for p, r in RULES]


def _keep_case(rep):
    return lambda m: rep[:1].upper() + rep[1:] if rep and m.group(0)[:1].isupper() else rep


def soften(x):
    """The text with the soft words; lists, tuples and dicts are softened all through."""
    if isinstance(x, str):
        for rx, rep in _COMPILED:
            x = rx.sub(_keep_case(rep), x)
        return x
    if isinstance(x, (list, tuple)):
        return type(x)(soften(v) for v in x)
    if isinstance(x, dict):
        return {k: soften(v) for k, v in x.items()}
    return x


def soft(fn):
    """Decorator: soften whatever a prompt function returns."""
    def wrapped(*a, **k):
        return soften(fn(*a, **k))
    wrapped.__name__, wrapped.__doc__ = fn.__name__, fn.__doc__
    return wrapped


def rules_js():
    """A JS function soft(text) for a published page, with the same rules."""
    return ("const SOFT=" + json.dumps(RULES) + ".map(([p,r])=>[new RegExp(p,'gi'),r]);"
            "const soft=(t)=>SOFT.reduce((s,[x,r])=>s.replace(x,(m)=>r&&m[0]!==m[0].toLowerCase()"
            "?r[0].toUpperCase()+r.slice(1):r),t);")
