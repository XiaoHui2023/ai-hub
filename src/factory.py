import logging
from config import Config
from core.services.registry import get as get_cls
from core.services.base_operation import BaseOperation

logger = logging.getLogger(__name__)


def create_operation(
    cfg: Config,
    service: str,
    operation: str,
    provider: str,
    model: str,
    stream: bool = False,
    **kwargs,
) -> BaseOperation:
    """
    根据 config 组装一个可运行的 Operation 实例

    cfg: 应用配置
    service: 服务名 (chat, search, ...)
    operation: 操作名 (completion, query, ...)
    provider: 提供商名 (grok, openai, aliyun, ...)
    model: 模型名
    stream: 客户端是否请求流式传输
    **kwargs: 传递给实现类构造函数的额外参数 (path, params, ...)
    """
    # 验证 model 是否在服务允许列表中
    if service not in cfg.services:
        raise KeyError(f"服务 '{service}' 未在 config 中配置")
    service_cfg = cfg.services[service]

    # config 获取 provider 配置
    if provider not in cfg.providers:
        raise KeyError(
            f"provider '{provider}' 未在 config 中配置，"
            f"已配置的 provider: {cfg.providers.configured_names}"
        )
    provider_cfg = cfg.providers[provider]

    if provider not in service_cfg:
        raise KeyError(
            f"服务 '{service}' 未配置 provider '{provider}'，"
            f"该服务已配置的 provider: {service_cfg.configured_names}"
        )
    allowed_models = service_cfg[provider].models
    if allowed_models and model not in allowed_models:
        raise ValueError(
            f"模型 '{model}' 不在服务 '{service}' 的 '{provider}' 允许列表中，"
            f"可用: {allowed_models}"
        )

    # 解析 stream：config 支持 AND 客户端请求
    use_stream = service_cfg[provider].stream and stream

    # 解析代理
    proxy = provider_cfg.proxy
    if proxy is None and provider_cfg.use_proxy:
        proxy = cfg.proxy

    # 获取 Key 轮询池 & 首个 api_key
    key_pool = provider_cfg.key_pool if provider_cfg.api_keys else None
    api_key = key_pool.next() if key_pool else None

    # 由 provider config 计算请求头
    headers = provider_cfg.get_headers(api_key) if api_key else None

    # 构造实例
    cls = get_cls(service, operation, provider, model)
    instance = cls(
        base_url=provider_cfg.base_url,
        api_key=api_key,
        key_pool=key_pool,
        headers=headers,
        model=model,
        proxy=proxy,
        stream=use_stream,
        **kwargs,
    )

    logger.debug(
        f"创建 operation: service={service}, operation={operation}, "
        f"provider={provider}, model={model}, cls={cls.__name__}"
    )

    return instance
