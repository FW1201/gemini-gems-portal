#!/usr/bin/env python3
"""CLI runner for tw-edu-chatgpt-usecases."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def load_spec(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_set_args(items: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --set value '{item}', expected key=value")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid --set key in '{item}'")
        values[key] = value.strip()
    return values


def find_scenario(spec: dict, scenario_id: str) -> dict:
    for scenario in spec.get("scenarios", []):
        if scenario.get("id") == scenario_id:
            return scenario
    raise KeyError(f"Scenario id not found: {scenario_id}")


def render_template(template: str, values: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        return values.get(key, f"{{{{{key}}}}}")

    return re.sub(r"\{\{\s*([^{}]+?)\s*\}\}", replace, template)


def cmd_list(spec: dict) -> int:
    for scenario in spec.get("scenarios", []):
        print(f"{scenario['id']}\t{scenario['name']}\t[{scenario['category']}]")
    return 0


def cmd_show(spec: dict, scenario_id: str) -> int:
    scenario = find_scenario(spec, scenario_id)
    print(json.dumps(scenario, ensure_ascii=False, indent=2))
    return 0


def cmd_render(spec: dict, scenario_id: str, values: dict[str, str]) -> int:
    scenario = find_scenario(spec, scenario_id)
    missing = [k for k in scenario.get("required_inputs", []) if k not in values]
    rendered = render_template(scenario["prompt_template"], values)

    payload = {
        "skill_id": spec.get("skill_id"),
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "prompt": rendered,
        "missing_required_inputs": missing,
        "global_guardrails": spec.get("global_guardrails", []),
        "scenario_compliance_notes": scenario.get("compliance_notes", []),
        "human_checklist": scenario.get("human_checklist", []),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    default_spec = Path(__file__).resolve().parents[1] / "references" / "tw-edu-ai-skills.json"
    parser = argparse.ArgumentParser(description="Run Taiwan education AI skill scenarios")
    parser.add_argument("command", choices=["list", "show", "render"])
    parser.add_argument("--spec", default=str(default_spec), help="Path to JSON skill spec")
    parser.add_argument("--id", dest="scenario_id", help="Scenario id")
    parser.add_argument("--set", action="append", default=[], help="Set input value: key=value")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"Spec not found: {spec_path}", file=sys.stderr)
        return 1

    try:
        spec = load_spec(spec_path)
        if args.command == "list":
            return cmd_list(spec)

        if not args.scenario_id:
            print("--id is required for show/render", file=sys.stderr)
            return 1

        if args.command == "show":
            return cmd_show(spec, args.scenario_id)

        values = parse_set_args(args.set)
        return cmd_render(spec, args.scenario_id, values)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
