#!/usr/bin/env python3
"""
Batch Feature Advancement / 批量 Feature 推进

Advance multiple features at once from a JSON input file.

Usage:
    python scripts/batch_advance.py batch_advance.json
    python scripts/batch_advance.py batch_advance.json --dry-run

Input JSON format:
{
  "advancements": [
    {
      "feature_id": "CORE-001",
      "new_step": "story_defined",
      "pr": "#123",
      "branch": "feature/CORE-001",
      "author": "Agent PO",
      "notes": "User story completed"
    }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ADVANCE_SCRIPT = PROJECT_ROOT / "scripts" / "advance_feature.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch advance features from JSON file")
    parser.add_argument("input_file", help="JSON file with advancement list")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    advancements = data.get("advancements", [])
    if not advancements:
        print("❌ No advancements found in input file", file=sys.stderr)
        sys.exit(1)
    
    print(f"📋 Processing {len(advancements)} advancement(s)...\n")
    
    failed = []
    for i, adv in enumerate(advancements, 1):
        feature_id = adv.get("feature_id")
        new_step = adv.get("new_step")
        if not feature_id or not new_step:
            print(f"❌ [{i}/{len(advancements)}] Missing feature_id or new_step", file=sys.stderr)
            failed.append(adv)
            continue
        
        print(f"[{i}/{len(advancements)}] Advancing {feature_id} to {new_step}...")
        
        cmd = [sys.executable, str(ADVANCE_SCRIPT), feature_id, new_step]
        if adv.get("pr"):
            cmd.extend(["--pr", adv["pr"]])
        if adv.get("branch"):
            cmd.extend(["--branch", adv["branch"]])
        if adv.get("author"):
            cmd.extend(["--author", adv["author"]])
        if adv.get("notes"):
            cmd.extend(["--notes", adv["notes"]])
        if args.dry_run:
            cmd.append("--dry-run")
        
        try:
            result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False, capture_output=True, text=True)
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr, file=sys.stderr)
                failed.append(adv)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            failed.append(adv)
        
        print()
    
    if failed:
        print(f"⚠️  {len(failed)} advancement(s) failed", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ All advancements completed successfully!")


if __name__ == "__main__":
    main()


