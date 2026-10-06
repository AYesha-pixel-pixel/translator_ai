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
"""English-to-Arabic translation agent for HR communications."""

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from tools.glossary_tool import lookup_glossary_terms

load_dotenv()

# Swap the model via the TRANSLATOR_MODEL env var; set the default to whatever
# model your scaffold originally used.
MODEL = os.getenv("TRANSLATOR_MODEL", "gemini-2.5-flash")

INSTRUCTION = """
You are an internal translation assistant for the HR team. Translate English
messages into Arabic for employees.

Process:
1. Call lookup_glossary_terms with the full message. Use every returned
   Arabic term exactly as given.
2. Translate into Modern Standard Arabic with a polite, professional
   business tone. Keep the natural flow; do not translate word for word.
3. Keep unchanged: names, numbers, dates, times, URLs, email addresses,
   currency amounts, and product or company names.
4. Preserve structure: paragraphs, bullet points, headings.
5. Never add, remove or soften information. If the source is ambiguous,
   translate faithfully and flag it in the notes.
6. Address employees consistently in the plural (كم) unless the message is
   clearly written to one named person.
7. Translate for meaning, not word for word. Use natural workplace Arabic
   (for example "meet your team" = التعرف على فريقك).
8. For warnings, disciplinary or legal text, do not raise or lower severity.
   Match the source's level of formality and specificity. Do not turn
   "incidents" into "violations" or "may" into "will".
9. For team announcements, open with الزملاء الكرام،

If the message is not in English, say so briefly and do not translate.

Output format:
- Arabic translation first.
- Then a section titled "Original (English)" containing the source text.
- Then "Notes for HR" only if something needs flagging.

"""

root_agent = Agent(
    name="translation_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Translates English HR messages into Arabic using a company glossary.",
    instruction=INSTRUCTION,
    tools=[lookup_glossary_terms],
)

app = App(
    root_agent=root_agent,
    name="app",
)
