#!/usr/bin/env python3
"""
Quick test script for error handling module / 错误处理模块快速测试脚本

Usage / 用法:
    python3 test_error_handling.py
"""

import sys
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:3000"


def test_error_response_format(endpoint: str) -> bool:
    """Test error response follows standard format / 测试错误响应遵循标准格式"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        data = response.json()
        
        # Check if it's an error response / 检查是否是错误响应
        if data.get("error") or not data.get("ok", True):
            required_fields = ["error", "error_type", "message", "message_zh", "trace_id", "timestamp"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ {endpoint}: Missing fields / 缺少字段: {missing_fields}")
                return False
            else:
                print(f"✅ {endpoint}: Error response format correct / 错误响应格式正确")
                print(f"   Trace ID: {data.get('trace_id')}")
                return True
        else:
            # Success response should have trace_id / 成功响应应包含 trace_id
            if "trace_id" in data or "X-Trace-ID" in response.headers:
                print(f"✅ {endpoint}: Success response has trace_id / 成功响应包含 trace_id")
                return True
            else:
                print(f"⚠️  {endpoint}: Success response missing trace_id / 成功响应缺少 trace_id")
                return False
    except Exception as e:
        print(f"❌ {endpoint}: Error / 错误: {e}")
        return False


def test_trace_id_in_header(endpoint: str) -> bool:
    """Test trace_id in response header / 测试响应头中的 trace_id"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        
        if "X-Trace-ID" in response.headers:
            trace_id = response.headers["X-Trace-ID"]
            print(f"✅ {endpoint}: X-Trace-ID header present / X-Trace-ID 响应头存在: {trace_id}")
            return True
        else:
            print(f"⚠️  {endpoint}: X-Trace-ID header missing / X-Trace-ID 响应头缺失")
            return False
    except Exception as e:
        print(f"❌ {endpoint}: Error / 错误: {e}")
        return False


def test_bot_status_errors() -> bool:
    """Test bot status includes error information / 测试 bot 状态包含错误信息"""
    try:
        response = requests.get(f"{BASE_URL}/api/bot/status", timeout=5)
        data = response.json()
        
        if "errors" in data:
            errors = data["errors"]
            print(f"✅ /api/bot/status: Error information present / 错误信息存在")
            print(f"   Global alert: {errors.get('global_alert')}")
            print(f"   Instance errors: {len(errors.get('instance_errors', {}))}")
            return True
        else:
            print(f"⚠️  /api/bot/status: Error information missing / 错误信息缺失")
            return False
    except Exception as e:
        print(f"❌ /api/bot/status: Error / 错误: {e}")
        return False


def main():
    """Run all tests / 运行所有测试"""
    print("=" * 60)
    print("Error Handling Module Test / 错误处理模块测试")
    print("=" * 60)
    print()
    
    # Test endpoints / 测试端点
    endpoints = [
        "/api/hyperliquid/status",
        "/api/bot/status",
        "/api/hyperliquid/connection",
    ]
    
    results = []
    
    # Test error response format / 测试错误响应格式
    print("1. Testing error response format / 测试错误响应格式")
    print("-" * 60)
    for endpoint in endpoints:
        results.append(test_error_response_format(endpoint))
    print()
    
    # Test trace_id in headers / 测试响应头中的 trace_id
    print("2. Testing trace_id in response headers / 测试响应头中的 trace_id")
    print("-" * 60)
    for endpoint in endpoints:
        results.append(test_trace_id_in_header(endpoint))
    print()
    
    # Test bot status errors / 测试 bot 状态错误
    print("3. Testing bot status error information / 测试 bot 状态错误信息")
    print("-" * 60)
    results.append(test_bot_status_errors())
    print()
    
    # Summary / 总结
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results / 结果: {passed}/{total} tests passed / 测试通过")
    
    if passed == total:
        print("✅ All tests passed! / 所有测试通过！")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed / {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())


