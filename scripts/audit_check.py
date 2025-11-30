#!/usr/bin/env python3
"""
Structured Audit Check / 结构化审计检查

Validates the JSON control plane (manifest, module cards, progress index)
and ensures feature artifacts exist.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
MODULE_DIR = PROJECT_ROOT / "docs" / "modules"
ROADMAP_PATH = PROJECT_ROOT / "status" / "roadmap.json"
PROGRESS_PATH = PROJECT_ROOT / "docs" / "progress" / "progress_index.json"
PIPELINE_ORDER = [
    "spec_defined",
    "story_defined",
    "ac_defined",
    "contract_defined",
    "unit_test_written",
    "code_implemented",
    "code_reviewed",
    "unit_test_passed",
    "smoke_test_passed",
    "integration_passed",
    "docs_updated",
    "progress_logged",
    "ci_cd_passed",
]
ARTIFACT_STAGE = {
    "spec": "spec_defined",
    "story": "story_defined",
    "tests": "unit_test_written",
    "code": "code_implemented",
}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Invalid JSON: {path} -> {err}") from err


def collect_module_cards() -> Dict[str, Dict[str, Any]]:
    cards: Dict[str, Dict[str, Any]] = {}
    if not MODULE_DIR.exists():
        return cards
    for path in MODULE_DIR.glob("*.json"):
        payload = load_json(path)
        module_id = payload.get("id")
        if module_id:
            cards[module_id] = payload
    return cards


def artifact_required(current_step: str, artifact_key: str) -> bool:
    stage = ARTIFACT_STAGE.get(artifact_key)
    if stage is None:
        return False
    try:
        current_idx = PIPELINE_ORDER.index(current_step)
    except ValueError:
        current_idx = len(PIPELINE_ORDER)
    target_idx = PIPELINE_ORDER.index(stage)
    return current_idx > target_idx


def check_feature_artifacts(module_id: str, feature: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    artifacts = feature.get("artifacts", {})
    current_step = feature.get("current_step", "")
    for key in ARTIFACT_STAGE.keys():
        if not artifact_required(current_step, key):
            continue
        value = artifacts.get(key)
        if value in (None, "", []):
            issues.append(f"[{module_id}:{feature.get('id')}] Missing artifact reference for {key}")
            continue
        paths = value if isinstance(value, list) else [value]
        for rel in paths:
            if rel and not (PROJECT_ROOT / rel).exists():
                issues.append(f"[{module_id}:{feature.get('id')}] Expected artifact file missing: {rel}")
    return issues


def check_roadmap_alignment(cards: Dict[str, Dict[str, Any]]) -> List[str]:
    issues: List[str] = []
    roadmap = load_json(ROADMAP_PATH)
    if not roadmap:
        return ["Roadmap JSON missing or invalid"]
    valid_pairs = {(module_id, feature["id"])
                   for module_id, card in cards.items()
                   for feature in card.get("features", [])}
    for entry in roadmap.get("features", []):
        module_id = entry.get("module_id")
        feature_id = entry.get("id")
        if (module_id, feature_id) not in valid_pairs:
            issues.append(f"Roadmap entry {feature_id} not found in module cards or module mismatch")
    return issues


def check_progress_events(cards: Dict[str, Dict[str, Any]]) -> List[str]:
    issues: List[str] = []
    progress = load_json(PROGRESS_PATH)
    if not progress:
        return ["Progress index JSON missing or invalid"]
    known_features = {feature["id"]
                      for card in cards.values()
                      for feature in card.get("features", [])}
    for event in progress.get("events", []):
        for fid in event.get("feature_ids", []):
            if fid not in known_features:
                issues.append(f"Progress event {event.get('id')} references unknown feature {fid}")
    return issues


def main() -> None:
    print("🔍 Running structured audit / 运行结构化审计")
    cards = collect_module_cards()
    if not cards:
        print("❌ No module cards found under docs/modules")
        sys.exit(1)

    issues: List[str] = []
    for module_id, card in cards.items():
        for feature in card.get("features", []):
            issues.extend(check_feature_artifacts(module_id, feature))

    issues.extend(check_roadmap_alignment(cards))
    issues.extend(check_progress_events(cards))

    if issues:
        print("❗ Issues detected / 发现问题：")
        for entry in issues:
            print(f"   - {entry}")
        sys.exit(1)

    print("✅ All checks passed / 所有检查通过")


if __name__ == "__main__":
    main()

