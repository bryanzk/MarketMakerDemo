#!/usr/bin/env python3
"""
Feature Advancement Automation / Feature 推进自动化

Automates the feature advancement workflow:
1. Update module JSON (current_step)
2. Sync roadmap.json
3. Add event to progress_index.json
4. Run audit_check.py for validation

Usage:
    python scripts/advance_feature.py CORE-001 spec_defined
    python scripts/advance_feature.py CORE-001 story_defined --pr "#123" --branch "feature/CORE-001"
    python scripts/advance_feature.py CORE-001 code_implemented --author "Agent TRADING" --notes "Implementation complete"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
MODULE_DIR = PROJECT_ROOT / "docs" / "modules"
ROADMAP_PATH = PROJECT_ROOT / "status" / "roadmap.json"
PROGRESS_PATH = PROJECT_ROOT / "docs" / "progress" / "progress_index.json"
AUDIT_SCRIPT = PROJECT_ROOT / "scripts" / "audit_check.py"

PIPELINE_STEPS = [
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


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {path} -> {e}") from e


def save_json(path: Path, data: Dict[str, Any]) -> None:
    """Save JSON file with pretty formatting."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find_feature_in_modules(feature_id: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Find feature in module cards. Returns (module_id, feature_dict)."""
    if not MODULE_DIR.exists():
        return None, None
    
    for module_file in MODULE_DIR.glob("*.json"):
        module_data = load_json(module_file)
        module_id = module_data.get("id")
        if not module_id:
            continue
        
        for feature in module_data.get("features", []):
            if feature.get("id") == feature_id:
                return module_id, feature
    
    return None, None


def validate_step(step: str) -> bool:
    """Validate that step is in pipeline."""
    return step in PIPELINE_STEPS


def get_next_event_id(progress_data: Dict[str, Any]) -> str:
    """Generate next event ID (E-YYYY-NNNN)."""
    year = datetime.now(timezone.utc).year
    events = progress_data.get("events", [])
    max_num = 0
    for event in events:
        event_id = event.get("id", "")
        if event_id.startswith(f"E-{year}-"):
            try:
                num = int(event_id.split("-")[-1])
                max_num = max(max_num, num)
            except ValueError:
                pass
    return f"E-{year}-{max_num + 1:04d}"


def update_module_json(module_id: str, feature_id: str, new_step: str) -> None:
    """Update current_step in module JSON."""
    module_path = MODULE_DIR / f"{module_id}.json"
    if not module_path.exists():
        raise FileNotFoundError(f"Module card not found: {module_path}")
    
    module_data = load_json(module_path)
    features = module_data.get("features", [])
    
    updated = False
    for feature in features:
        if feature.get("id") == feature_id:
            old_step = feature.get("current_step", "")
            feature["current_step"] = new_step
            feature["last_updated"] = datetime.now(timezone.utc).isoformat()
            updated = True
            print(f"✅ Updated {module_id}.json: {feature_id} {old_step} → {new_step}")
            break
    
    if not updated:
        raise ValueError(f"Feature {feature_id} not found in {module_id}.json")
    
    save_json(module_path, module_data)


def sync_roadmap(feature_id: str, module_id: str, new_step: str) -> None:
    """Sync roadmap.json with module card."""
    roadmap = load_json(ROADMAP_PATH)
    features = roadmap.get("features", [])
    
    updated = False
    for entry in features:
        if entry.get("id") == feature_id and entry.get("module_id") == module_id:
            entry["current_step"] = new_step
            updated = True
            print(f"✅ Synced roadmap.json: {feature_id} → {new_step}")
            break
    
    if not updated:
        # Add new entry if not found
        roadmap.setdefault("features", []).append({
            "id": feature_id,
            "module_id": module_id,
            "current_step": new_step,
            "sync_source": f"docs/modules/{module_id}.json"
        })
        print(f"✅ Added new entry to roadmap.json: {feature_id}")
    
    roadmap["last_synced"] = datetime.now(timezone.utc).date().isoformat()
    save_json(ROADMAP_PATH, roadmap)


def add_progress_event(
    feature_id: str,
    module_id: str,
    new_step: str,
    event_type: str = "step_advance",
    pr: Optional[str] = None,
    branch: Optional[str] = None,
    author: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    """Add event to progress_index.json."""
    progress = load_json(PROGRESS_PATH)
    if not progress:
        progress = {"$schema": "https://json-schema.org/draft/2020-12/schema", "version": "1.0.0", "events": []}
    
    event_id = get_next_event_id(progress)
    event = {
        "id": event_id,
        "type": event_type,
        "feature_ids": [feature_id],
        "modules": [module_id],
        "summary": f"Advanced {feature_id} to {new_step}",
        "step": new_step,
        "author": author or "Agent PM",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if pr:
        event["pr"] = pr
    if branch:
        event["branch"] = branch
    if notes:
        event["notes"] = notes
    
    progress.setdefault("events", []).append(event)
    save_json(PROGRESS_PATH, progress)
    print(f"✅ Added progress event: {event_id}")


def run_audit() -> bool:
    """Run audit_check.py and return success status."""
    print("\n🔍 Running audit check...")
    try:
        result = subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Audit check failed: {e}", file=sys.stderr)
        return False


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Advance a feature to the next pipeline step",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("feature_id", help="Feature ID (e.g., CORE-001)")
    parser.add_argument("new_step", help=f"New step (one of: {', '.join(PIPELINE_STEPS)})")
    parser.add_argument("--pr", help="PR number (e.g., #123)")
    parser.add_argument("--branch", help="Git branch name")
    parser.add_argument("--author", help="Author name (default: Agent PM)")
    parser.add_argument("--notes", help="Additional notes")
    parser.add_argument("--skip-audit", action="store_true", help="Skip audit check")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without writing")
    
    args = parser.parse_args()
    
    # Validate step
    if not validate_step(args.new_step):
        print(f"❌ Invalid step: {args.new_step}", file=sys.stderr)
        print(f"   Valid steps: {', '.join(PIPELINE_STEPS)}", file=sys.stderr)
        sys.exit(1)
    
    # Find feature
    module_id, feature = find_feature_in_modules(args.feature_id)
    if not module_id or not feature:
        print(f"❌ Feature {args.feature_id} not found in any module card", file=sys.stderr)
        sys.exit(1)
    
    current_step = feature.get("current_step", "")
    print(f"📋 Feature: {args.feature_id} ({module_id})")
    print(f"   Current: {current_step}")
    print(f"   Target:  {args.new_step}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No files will be modified")
        return
    
    # Update module JSON
    try:
        update_module_json(module_id, args.feature_id, args.new_step)
    except Exception as e:
        print(f"❌ Failed to update module JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Sync roadmap
    try:
        sync_roadmap(args.feature_id, module_id, args.new_step)
    except Exception as e:
        print(f"❌ Failed to sync roadmap: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Add progress event
    try:
        add_progress_event(
            args.feature_id,
            module_id,
            args.new_step,
            pr=args.pr,
            branch=args.branch,
            author=args.author,
            notes=args.notes,
        )
    except Exception as e:
        print(f"❌ Failed to add progress event: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run audit
    if not args.skip_audit:
        if not run_audit():
            print("\n⚠️  Audit check failed. Please review the issues above.", file=sys.stderr)
            sys.exit(1)
    
    print("\n✅ Feature advancement complete!")


if __name__ == "__main__":
    main()



