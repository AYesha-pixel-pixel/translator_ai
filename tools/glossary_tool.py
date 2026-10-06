# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Glossary lookup tool for translating specialized terminology."""

import csv
import re
from pathlib import Path
from typing import Any

# Default path to the glossary CSV file
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_GLOSSARY_PATH = _PROJECT_ROOT / "data" / "glossary.csv"

# Global module cache for loaded glossary entries
_CACHED_GLOSSARY: list[dict[str, Any]] | None = None


def _word_to_pattern(w: str, is_last: bool) -> str:
    """Builds a plural-tolerant regex pattern chunk for a single word."""
    if not is_last:
        return re.escape(w)

    lower = w.lower()
    # e.g., 'salaries' -> match 'salaries' or singular 'salary'
    if lower.endswith("ies") and len(lower) > 3:
        sing = re.escape(w[:-3] + "y")
        return f"(?:{re.escape(w)}|{sing})"
    # e.g., 'salary' -> match 'salaries', 'salary', 'salarys'
    if lower.endswith("y") and len(lower) > 1 and lower[-2] not in "aeiou":
        plur = re.escape(w[:-1] + "ies")
        return f"(?:{plur}|{re.escape(w)}s?)"
    # e.g., 'processes', 'boxes' -> match full word or singular
    if lower.endswith(("sses", "shes", "ches", "xes", "zes")):
        sing = re.escape(w[:-2])
        return f"(?:{re.escape(w)}|{sing})"
    # e.g., 'box', 'tax' -> match 'box', 'boxes'
    if lower.endswith(("ss", "sh", "ch", "x", "z")):
        return f"{re.escape(w)}(?:es)?"
    # e.g., 'benefits', 'hours', 'resources' -> match 'benefit', 'benefits'
    if lower.endswith("s") and not lower.endswith("ss"):
        sing = re.escape(w[:-1])
        return f"{sing}(?:s|es)?"
    # Default standard noun: 'contract' -> match 'contract', 'contracts'
    return f"{re.escape(w)}(?:s|es)?"


def _term_to_regex(term: str) -> re.Pattern[str]:
    """Compiles a case-insensitive, whole-word regex pattern for a glossary term."""
    tokens = re.split(r"([-\s]+)", term)
    pattern_parts: list[str] = []
    word_indices = [i for i, t in enumerate(tokens) if re.search(r"\w", t)]
    last_word_idx = max(word_indices) if word_indices else -1

    for i, token in enumerate(tokens):
        if re.search(r"^[- \t]+$", token):
            pattern_parts.append(r"[-\s]+")
        else:
            pattern_parts.append(_word_to_pattern(token, is_last=(i == last_word_idx)))

    joined = "".join(pattern_parts)
    return re.compile(rf"\b{joined}\b", re.IGNORECASE)


def compile_glossary_entry(
    english_term: str,
    arabic_term: str,
    notes: str = "",
) -> dict[str, Any]:
    """Creates a compiled glossary entry ready for fast matching."""
    clean_en = english_term.strip()
    clean_ar = arabic_term.strip()
    return {
        "english": clean_en,
        "arabic": clean_ar,
        "notes": notes.strip(),
        "regex": _term_to_regex(clean_en),
    }


def load_glossary(csv_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Loads glossary terms from a CSV file and compiles their regexes."""
    path = Path(csv_path) if csv_path else _DEFAULT_GLOSSARY_PATH
    if not path.is_file():
        return []

    entries: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row.get("english_term", "")
            ar = row.get("arabic_term", "")
            notes = row.get("notes", "")
            if en and ar:
                entries.append(compile_glossary_entry(en, ar, notes))

    # Sort longest English terms first so longer phrases win over shorter overlaps
    entries.sort(key=lambda item: len(item["english"]), reverse=True)
    return entries


def get_glossary(csv_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Returns the cached glossary list, loading it from CSV once if not yet cached."""
    global _CACHED_GLOSSARY
    if _CACHED_GLOSSARY is not None and csv_path is None:
        return _CACHED_GLOSSARY

    loaded = load_glossary(csv_path)
    if csv_path is None:
        _CACHED_GLOSSARY = loaded
    return loaded


def find_glossary_matches(
    message: str,
    glossary_entries: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    """Finds glossary matches in a message resolving overlaps and duplicates."""
    if not message or not isinstance(message, str):
        return []

    entries = glossary_entries if glossary_entries is not None else get_glossary()
    if not entries:
        return []

    # Ensure entries are sorted longest term first
    sorted_entries = sorted(
        entries, key=lambda item: len(item["english"]), reverse=True
    )

    accepted_spans: list[tuple[int, int]] = []
    matched_items: list[tuple[int, dict[str, Any]]] = []

    for entry in sorted_entries:
        regex: re.Pattern[str] = entry["regex"]
        for match in regex.finditer(message):
            start, end = match.start(), match.end()

            # Skip if this match overlaps with any previously accepted (longer) span
            if any(
                max(start, span_start) < min(end, span_end)
                for span_start, span_end in accepted_spans
            ):
                continue

            accepted_spans.append((start, end))
            matched_items.append((start, entry))

    # Sort by appearance in the message text
    matched_items.sort(key=lambda item: item[0])

    # Deduplicate terms while preserving order of appearance
    seen_english: set[str] = set()
    results: list[dict[str, str]] = []
    for _, entry in matched_items:
        english = entry["english"]
        if english not in seen_english:
            seen_english.add(english)
            results.append({"english": english, "arabic": entry["arabic"]})

    return results


def lookup_glossary_terms(message: str) -> dict:
    """Finds glossary terms in a message and returns their Arabic translations.

    Scans the input message for human resources (HR) terminology defined in the glossary.
    The tool performs case-insensitive, whole-word matching, handles simple plural forms,
    and resolves overlaps by prioritizing longer compound terms (e.g. 'end-of-service benefits'
    over shorter overlapping sub-terms).

    Args:
        message: The text string to search for glossary terms.

    Returns:
        A dictionary containing a list of unique matched terms with their English
        and Arabic translations:
        {"matches": [{"english": "annual leave", "arabic": "الإجازة السنوية"}]}
        Returns {"matches": []} if no terms match.
    """
    matches = find_glossary_matches(message)
    return {"matches": matches}
