# -*- coding: utf-8 -*-
"""服务商配置，内置 anyrouter / agentrouter，支持自定义扩展"""

from dataclasses import dataclass


@dataclass
class ProviderConfig:
    domain:        str
    sign_in_path:  str = "/api/user/sign_in"
    user_info_path: str = "/api/user/self"
    api_user_key:  str = "new-api-user"


# 内置服务商
BUILTIN_PROVIDERS: dict[str, ProviderConfig] = {
    "anyrouter": ProviderConfig(
        domain="https://anyrouter.top",
    ),
    "agentrouter": ProviderConfig(
        domain="https://agentrouter.org",
    ),
}


def get_provider(name: str, custom=None) -> ProviderConfig:
    """
    获取服务商配置。
    自定义格式（通过环境变量 PROVIDERS 传入）：
    {
        "myrouter": {
            "domain": "https://my.example.com",
            "sign_in_path": "/api/checkin",
            ...
        }
    }
    """
    # 优先使用自定义配置
    if custom and name in custom:
        c = custom[name]
        return ProviderConfig(
            domain=c["domain"],
            sign_in_path=c.get("sign_in_path", "/api/user/sign_in"),
            user_info_path=c.get("user_info_path", "/api/user/self"),
            api_user_key=c.get("api_user_key", "new-api-user"),
        )

    if name in BUILTIN_PROVIDERS:
        return BUILTIN_PROVIDERS[name]

    raise ValueError(f"未知服务商: {name}，请在 PROVIDERS 环境变量中配置")
