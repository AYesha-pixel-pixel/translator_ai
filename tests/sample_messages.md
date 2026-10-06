# Translation agent: test messages

Paste each message into the agent (`adk web`) one at a time.

## 1. Policy update with dates and numbers
Dear team, effective 1 November 2026, the annual leave entitlement will increase from 21 to 24 days per year. Leave requests must be submitted at least 14 days in advance. The updated policy is effective for all full-time staff.

**Check:** dates and numbers unchanged (1 November 2026, 21, 24, 14); "annual leave" uses the glossary term.

## 2. Glossary terms in different forms
All new hires must complete their Probation Period before applying for Annual Leaves. Salaries are paid on the 25th of each month. Overtime must be approved in advance. End-of-service benefits are calculated according to the Employment Contract.

**Check:** every glossary term uses the exact glossary Arabic, including the plural ("Annual Leaves", "Salaries") and the capitalized forms.

## 3. Names, email address and URL
Hi all, please send your signed forms to Sarah Mitchell at sarah.mitchell@acme-corp.com by Friday, or upload them at https://hr.acme-corp.com/forms. For help, contact Ahmed Khan on extension 4417.

**Check:** names, email, URL and extension left exactly as written.

## 4. Longer message with a bullet list
Welcome to the company! Your first week will look like this:
- Monday: Orientation with Human Resources and a tour of the office
- Tuesday: IT setup and system access
- Wednesday: Meet your team and review your working hours
- Thursday: Safety training (mandatory, 2 hours)
- Friday: Check-in with your manager

Please bring your ID and signed Employment Contract on the first day.

**Check:** bullet structure preserved, days and numbers unchanged, glossary terms used.

## 5. Sensitive disciplinary notice
This letter is a formal notice of disciplinary action following repeated late arrivals during the past month. Please note that further incidents may result in additional action. You are invited to discuss this matter with HR within 5 working days.

**Check:** tone is formal and firm, nothing softened or added, "disciplinary action" uses the glossary term.

## Edge cases (optional)
- **No glossary terms:** "The office will be closed this Thursday for maintenance." The agent should still translate, and the glossary tool should return no matches.
- **Not English:** paste a short Arabic sentence. The agent should say it is not English and not translate it.

## For every message, also check
- The glossary tool was called (visible in the dev UI trace).
- Output order: Arabic, then "Original (English)", then "Notes for HR" only if needed.
- A native Arabic speaker reviews the tone and fluency.
