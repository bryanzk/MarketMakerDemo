"""
Unit tests for HyperliquidClient signature generation
HyperliquidClient 签名生成单元测试

Tests for Ethereum signature generation for Hyperliquid API
测试 Hyperliquid API 的以太坊签名生成

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidSignature:
    """Test signature generation for Hyperliquid API / 测试 Hyperliquid API 的签名生成"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid private key format
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", True)
    def test_signature_generation_with_eth_account(self, mock_post):
        """Test signature generation when eth_account is available / 测试 eth_account 可用时的签名生成"""
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        # Verify account is initialized / 验证账户已初始化
        assert client._account is not None

        # Test signature generation / 测试签名生成
        action = {"type": "order", "orders": []}
        nonce = 1234567890

        signature = client._generate_signature(action, nonce)

        # Verify signature is generated / 验证签名已生成
        assert signature is not None
        assert "r" in signature
        assert "s" in signature
        assert "v" in signature
        assert isinstance(signature["r"], str)
        assert isinstance(signature["s"], str)
        assert isinstance(signature["v"], int)

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", False)
    def test_signature_generation_without_eth_account(self, mock_post):
        """Test signature generation when eth_account is not available / 测试 eth_account 不可用时的签名生成"""
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        # Test signature generation / 测试签名生成
        action = {"type": "order", "orders": []}
        nonce = 1234567890

        signature = client._generate_signature(action, nonce)

        # Verify signature is None when eth_account is not available / 验证 eth_account 不可用时签名为 None
        assert signature is None

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", True)
    def test_signature_different_for_different_actions(self, mock_post):
        """Test that different actions generate different signatures / 测试不同操作生成不同签名"""
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        action1 = {"type": "order", "orders": [{"a": 100}]}
        action2 = {"type": "order", "orders": [{"a": 200}]}
        nonce = 1234567890

        signature1 = client._generate_signature(action1, nonce)
        signature2 = client._generate_signature(action2, nonce)

        # Verify signatures are different / 验证签名不同
        assert signature1 is not None
        assert signature2 is not None
        assert signature1 != signature2

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", True)
    def test_signature_different_for_different_nonces(self, mock_post):
        """Test that different nonces generate different signatures / 测试不同 nonce 生成不同签名"""
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        action = {"type": "order", "orders": []}
        nonce1 = 1234567890
        nonce2 = 1234567891

        signature1 = client._generate_signature(action, nonce1)
        signature2 = client._generate_signature(action, nonce2)

        # Verify signatures are different / 验证签名不同
        assert signature1 is not None
        assert signature2 is not None
        assert signature1 != signature2


class TestHyperliquidOrderPayload:
    """Test order payload building with signature / 测试带签名的订单负载构建"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", True)
    def test_order_payload_includes_signature(self, mock_post):
        """Test that order payload includes signature field / 测试订单负载包含签名字段"""
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        order = {
            "side": "buy",
            "type": "limit",
            "price": 100.0,
            "quantity": 1.0,
        }

        payload = client._build_order_payload(order)

        # Verify payload structure / 验证负载结构
        assert "action" in payload
        assert "nonce" in payload
        assert "vaultAddress" in payload

        # Verify signature is included if eth_account is available / 验证 eth_account 可用时包含签名
        if client._account is not None:
            assert "signature" in payload
            assert payload["signature"] is not None
            assert "r" in payload["signature"]
            assert "s" in payload["signature"]
            assert "v" in payload["signature"]

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", False)
    def test_order_payload_without_signature(self, mock_post):
        """Test order payload when signature cannot be generated / 测试无法生成签名时的订单负载"""
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        order = {
            "side": "buy",
            "type": "limit",
            "price": 100.0,
            "quantity": 1.0,
        }

        payload = client._build_order_payload(order)

        # Verify payload structure / 验证负载结构
        assert "action" in payload
        assert "nonce" in payload
        assert "vaultAddress" in payload

        # Signature may not be included if eth_account is not available / 如果 eth_account 不可用，签名可能不包含
        # But payload should still be valid / 但负载应该仍然有效
        assert payload["action"]["type"] == "order"



