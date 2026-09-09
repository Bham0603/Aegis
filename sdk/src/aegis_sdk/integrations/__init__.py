"""
Aegis SDK framework integrations.

Optional adapters for popular agent frameworks.
Each adapter is imported lazily to avoid requiring all framework
dependencies in the core SDK.
"""

from aegis_sdk.integrations.mcp import AegisMCPGateway