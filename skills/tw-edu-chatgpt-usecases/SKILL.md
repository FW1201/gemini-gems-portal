---
name: tw-edu-chatgpt-usecases
description: Structured Taiwan education ChatGPT use-case library for lesson planning, competency-based question generation, and school administration drafting. Use when users need localized zh-TW school workflows, prompt templates, guardrails, or reusable scenario packs that align with Taiwan curriculum and policy context.
---

# Taiwan Education ChatGPT Usecases

Load this skill when the user needs practical Taiwan school scenarios for using ChatGPT in teaching, assessment, or administration.

## Workflow

1. Read `references/tw-edu-ai-skills.json`.
2. Select scenario(s) by `id`, `name`, or `category`.
3. Ask only for missing required inputs.
4. Render the `prompt_template` with user inputs.
5. Always include `global_guardrails` and scenario-level `compliance_notes`.
6. Require human review using `human_checklist` before final use.

## Fast CLI helper

Use `scripts/run_tw_edu_skill.py`:

- `python3 scripts/run_tw_edu_skill.py list`
- `python3 scripts/run_tw_edu_skill.py show --id tw-lesson-weekly-plan`
- `python3 scripts/run_tw_edu_skill.py render --id tw-lesson-weekly-plan --set grade=國小五年級 --set subject=自然 --set unit=水溶液 --set periods=4`

## Output rules

- Keep output in Traditional Chinese unless user asks otherwise.
- Do not fabricate policy claims; keep source links attached when requested.
- Treat all generated content as draft-only.
