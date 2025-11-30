#!/usr/bin/env python3
"""
Audit Check Script / 审计检查脚本

Scans the project to identify:
- Missing specs for features
- Missing tests for implemented code
- Missing documentation
- Status inconsistencies in roadmap.json

Usage:
    python scripts/audit_check.py
    python scripts/audit_check.py --fix  # Auto-fix some issues
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Project root
PROJECT_ROOT = Path(__file__).parent.parent


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {path}: {e}")
        return {}


def check_roadmap_artifacts() -> list[dict]:
    """Check if all artifacts defined in roadmap.json exist."""
    issues = []
    roadmap = load_json(PROJECT_ROOT / "status" / "roadmap.json")
    
    if not roadmap:
        issues.append({
            "type": "MISSING_FILE",
            "severity": "critical",
            "file": "status/roadmap.json",
            "message": "Roadmap file is missing or invalid"
        })
        return issues
    
    for feature in roadmap.get("features", []):
        feature_id = feature.get("id", "UNKNOWN")
        artifacts = feature.get("artifacts", {})
        status = feature.get("status", {})
        
        # Check spec file
        if status.get("spec_defined") and artifacts.get("spec"):
            spec_path = PROJECT_ROOT / artifacts["spec"]
            if not spec_path.exists():
                issues.append({
                    "type": "MISSING_ARTIFACT",
                    "severity": "warning",
                    "feature": feature_id,
                    "artifact": "spec",
                    "expected_path": artifacts["spec"],
                    "message": f"Spec marked as defined but file missing: {artifacts['spec']}"
                })
        
        # Check test file
        if status.get("unit_test_written") and artifacts.get("test"):
            test_path = PROJECT_ROOT / artifacts["test"]
            if not test_path.exists():
                issues.append({
                    "type": "MISSING_ARTIFACT",
                    "severity": "warning",
                    "feature": feature_id,
                    "artifact": "test",
                    "expected_path": artifacts["test"],
                    "message": f"Test marked as written but file missing: {artifacts['test']}"
                })
        
        # Check code file
        if status.get("code_implemented") and artifacts.get("code"):
            code_path = PROJECT_ROOT / artifacts["code"]
            if not code_path.exists():
                issues.append({
                    "type": "MISSING_ARTIFACT",
                    "severity": "warning",
                    "feature": feature_id,
                    "artifact": "code",
                    "expected_path": artifacts["code"],
                    "message": f"Code marked as implemented but file missing: {artifacts['code']}"
                })
    
    return issues


def check_pipeline_order() -> list[dict]:
    """Check if pipeline steps are in correct order."""
    issues = []
    roadmap = load_json(PROJECT_ROOT / "status" / "roadmap.json")
    
    if not roadmap:
        return issues
    
    # Define step order
    step_order = [
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
        "ci_cd_passed"
    ]
    
    for feature in roadmap.get("features", []):
        feature_id = feature.get("id", "UNKNOWN")
        status = feature.get("status", {})
        
        # Check for skipped steps
        found_true = False
        for i, step in enumerate(step_order):
            if status.get(step):
                found_true = True
            elif found_true:
                # Found a false after a true - check if it's a later step
                for j in range(i + 1, len(step_order)):
                    if status.get(step_order[j]):
                        issues.append({
                            "type": "SKIPPED_STEP",
                            "severity": "error",
                            "feature": feature_id,
                            "skipped_step": step,
                            "later_step": step_order[j],
                            "message": f"Step '{step}' is false but later step '{step_order[j]}' is true"
                        })
                        break
    
    return issues


def check_contracts() -> list[dict]:
    """Check if all contract files exist and are valid."""
    issues = []
    contracts_dir = PROJECT_ROOT / "contracts"
    
    expected_contracts = ["trading.json", "portfolio.json", "web.json", "ai.json"]
    
    for contract_file in expected_contracts:
        contract_path = contracts_dir / contract_file
        if not contract_path.exists():
            issues.append({
                "type": "MISSING_CONTRACT",
                "severity": "error",
                "file": f"contracts/{contract_file}",
                "message": f"Contract file missing: {contract_file}"
            })
        else:
            contract = load_json(contract_path)
            if not contract.get("interfaces") and not contract.get("api_endpoints"):
                issues.append({
                    "type": "EMPTY_CONTRACT",
                    "severity": "warning",
                    "file": f"contracts/{contract_file}",
                    "message": f"Contract file has no interfaces defined: {contract_file}"
                })
    
    return issues


def check_module_cards() -> list[dict]:
    """Check if all module card files exist."""
    issues = []
    modules_dir = PROJECT_ROOT / "docs" / "modules"
    
    expected_modules = ["trading.json", "portfolio.json", "web.json", "ai.json"]
    
    for module_file in expected_modules:
        module_path = modules_dir / module_file
        if not module_path.exists():
            issues.append({
                "type": "MISSING_MODULE_CARD",
                "severity": "warning",
                "file": f"docs/modules/{module_file}",
                "message": f"Module card missing: {module_file}"
            })
    
    return issues


def check_test_coverage() -> list[dict]:
    """Check if tests exist for implemented features."""
    issues = []
    roadmap = load_json(PROJECT_ROOT / "status" / "roadmap.json")
    
    if not roadmap:
        return issues
    
    for feature in roadmap.get("features", []):
        feature_id = feature.get("id", "UNKNOWN")
        status = feature.get("status", {})
        artifacts = feature.get("artifacts", {})
        
        # If code is implemented but no test exists
        if status.get("code_implemented") and not status.get("unit_test_written"):
            issues.append({
                "type": "MISSING_TEST",
                "severity": "error",
                "feature": feature_id,
                "message": f"Code implemented but unit test not written (TDD violation)"
            })
    
    return issues


def print_report(issues: list[dict]) -> None:
    """Print audit report."""
    print("\n" + "=" * 60)
    print("📋 AUDIT REPORT / 审计报告")
    print("=" * 60)
    
    if not issues:
        print("\n✅ No issues found! / 未发现问题！\n")
        return
    
    # Group by severity
    critical = [i for i in issues if i.get("severity") == "critical"]
    errors = [i for i in issues if i.get("severity") == "error"]
    warnings = [i for i in issues if i.get("severity") == "warning"]
    
    print(f"\n📊 Summary / 摘要:")
    print(f"   🔴 Critical: {len(critical)}")
    print(f"   🟠 Errors: {len(errors)}")
    print(f"   🟡 Warnings: {len(warnings)}")
    print(f"   Total: {len(issues)}")
    
    if critical:
        print("\n🔴 CRITICAL ISSUES:")
        for issue in critical:
            print(f"   - [{issue['type']}] {issue['message']}")
    
    if errors:
        print("\n🟠 ERRORS:")
        for issue in errors:
            print(f"   - [{issue['type']}] {issue.get('feature', '')} {issue['message']}")
    
    if warnings:
        print("\n🟡 WARNINGS:")
        for issue in warnings:
            print(f"   - [{issue['type']}] {issue.get('feature', '')} {issue['message']}")
    
    print("\n" + "=" * 60)


def main():
    """Run all audit checks."""
    print("🔍 Running audit checks... / 运行审计检查...")
    
    all_issues = []
    
    # Run all checks
    print("   Checking roadmap artifacts...")
    all_issues.extend(check_roadmap_artifacts())
    
    print("   Checking pipeline order...")
    all_issues.extend(check_pipeline_order())
    
    print("   Checking contracts...")
    all_issues.extend(check_contracts())
    
    print("   Checking module cards...")
    all_issues.extend(check_module_cards())
    
    print("   Checking test coverage...")
    all_issues.extend(check_test_coverage())
    
    # Print report
    print_report(all_issues)
    
    # Exit with error code if critical issues found
    critical_count = len([i for i in all_issues if i.get("severity") == "critical"])
    error_count = len([i for i in all_issues if i.get("severity") == "error"])
    
    if critical_count > 0:
        sys.exit(2)
    elif error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

