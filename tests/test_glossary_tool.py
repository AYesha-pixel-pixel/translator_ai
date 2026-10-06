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
"""Unit tests for the glossary lookup tool."""

import pytest

from tools.glossary_tool import (
    compile_glossary_entry,
    lookup_glossary_terms,
)


def test_exact_match() -> None:
    """Tests exact matching of glossary terms in a message."""
    message = "The probation period is three months from the start date."
    result = lookup_glossary_terms(message)
    assert result == {
        "matches": [{"english": "probation period", "arabic": "فترة التجربة"}]
    }

    message2 = "She officially submitted her resignation yesterday."
    result2 = lookup_glossary_terms(message2)
    assert result2 == {"matches": [{"english": "resignation", "arabic": "الاستقالة"}]}


def test_plural() -> None:
    """Tests that the tool matches simple plural and singular variations."""
    # Plural of 'employment contract' -> 'employment contracts'
    message = "All new employment contracts must be reviewed by legal."
    result = lookup_glossary_terms(message)
    assert result == {
        "matches": [{"english": "employment contract", "arabic": "عقد العمل"}]
    }

    # Plural of 'salary' -> 'salaries'
    message2 = "The management team decided to review all employee salaries."
    result2 = lookup_glossary_terms(message2)
    assert result2 == {"matches": [{"english": "salary", "arabic": "الراتب"}]}

    # Singular form of an already plural glossary term: 'end-of-service benefit'
    message3 = "He is entitled to an end-of-service benefit under labor law."
    result3 = lookup_glossary_terms(message3)
    assert result3 == {
        "matches": [
            {"english": "end-of-service benefits", "arabic": "مكافأة نهاية الخدمة"}
        ]
    }

    # Singular form of 'working hours' -> 'working hour'
    message4 = "The standard working hour policy is forty hours per week."
    result4 = lookup_glossary_terms(message4)
    assert result4 == {
        "matches": [{"english": "working hours", "arabic": "ساعات العمل"}]
    }


def test_capitalized_term() -> None:
    """Tests case-insensitive matching for all-caps, title-case, and mixed-case."""
    # All uppercase
    message = "Please contact HUMAN RESOURCES regarding benefits."
    result = lookup_glossary_terms(message)
    assert result == {
        "matches": [{"english": "Human Resources", "arabic": "الموارد البشرية"}]
    }

    # Title case
    message2 = "The Notice Period for senior employees is two months."
    result2 = lookup_glossary_terms(message2)
    assert result2 == {
        "matches": [{"english": "notice period", "arabic": "فترة الإشعار"}]
    }

    # Mixed case with hyphen
    message3 = "Details on Disciplinary Action are in the employee handbook."
    result3 = lookup_glossary_terms(message3)
    assert result3 == {
        "matches": [{"english": "disciplinary action", "arabic": "الإجراء التأديبي"}]
    }


def test_two_terms_in_one_message() -> None:
    """Tests finding multiple distinct glossary terms within a single message."""
    message = "His salary and annual leave were confirmed in the offer letter."
    result = lookup_glossary_terms(message)
    assert result == {
        "matches": [
            {"english": "salary", "arabic": "الراتب"},
            {"english": "annual leave", "arabic": "الإجازة السنوية"},
        ]
    }

    message2 = "Employees can take sick leave or request a grace period if unwell."
    result2 = lookup_glossary_terms(message2)
    assert result2 == {
        "matches": [
            {"english": "sick leave", "arabic": "الإجازة المرضية"},
            {"english": "grace period", "arabic": "فترة السماح"},
        ]
    }


def test_overlapping_terms(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests that longest terms win over shorter overlapping terms."""
    # Custom glossary containing overlapping terms
    custom_glossary = [
        compile_glossary_entry("end-of-service benefits", "مكافأة نهاية الخدمة"),
        compile_glossary_entry("benefits", "مزايا"),
        compile_glossary_entry("service", "خدمة"),
        compile_glossary_entry("employment contract", "عقد العمل"),
        compile_glossary_entry("contract", "عقد"),
    ]
    monkeypatch.setattr(
        "tools.glossary_tool.get_glossary", lambda *args, **kwargs: custom_glossary
    )

    # 1. 'end-of-service benefits' should win over 'benefits' and 'service'
    msg1 = "The employee is entitled to end-of-service benefits upon retirement."
    res1 = lookup_glossary_terms(msg1)
    assert res1 == {
        "matches": [
            {"english": "end-of-service benefits", "arabic": "مكافأة نهاية الخدمة"}
        ]
    }

    # 2. 'employment contract' should win over 'contract'
    msg2 = "Please sign the employment contract."
    res2 = lookup_glossary_terms(msg2)
    assert res2 == {
        "matches": [{"english": "employment contract", "arabic": "عقد العمل"}]
    }

    # 3. When the shorter term appears outside the overlap, both are matched
    msg3 = "End-of-service benefits and healthcare benefits are provided."
    res3 = lookup_glossary_terms(msg3)
    assert res3 == {
        "matches": [
            {"english": "end-of-service benefits", "arabic": "مكافأة نهاية الخدمة"},
            {"english": "benefits", "arabic": "مزايا"},
        ]
    }


def test_no_match() -> None:
    """Tests that non-matching messages return an empty list."""
    message = "Good morning! Can you check tomorrow's weather forecast?"
    result = lookup_glossary_terms(message)
    assert result == {"matches": []}

    # Empty string and whitespace
    assert lookup_glossary_terms("") == {"matches": []}
    assert lookup_glossary_terms("   ") == {"matches": []}

    # Partial substring that is not a whole word
    assert lookup_glossary_terms("oversalary payments are prohibited") == {
        "matches": []
    }
    assert lookup_glossary_terms("homesick leave was requested") == {"matches": []}


def test_no_duplicate_matches() -> None:
    """Tests that repeating a term multiple times produces no duplicates."""
    message = "His salary was discussed, and a new salary was agreed upon."
    result = lookup_glossary_terms(message)
    assert result == {"matches": [{"english": "salary", "arabic": "الراتب"}]}
