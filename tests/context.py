import json
import argparse
from typing import Type
from urllib import request, error

from pydantic import BaseModel

from ai_hub_protocol.context.add import Request as AddRequest, Response as AddResponse
from ai_hub_protocol.context.search import Request as SearchRequest, Response as SearchResponse


def build_request(url: str, payload: dict) -> request.Request:
    return request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def send(url: str, payload: dict, response_model: Type[BaseModel] = None) -> None:
    """发送请求并打印结果"""
    req = build_request(url, payload)
    try:
        with request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="ignore"))
            if response_model:
                result = response_model.model_validate(body)
                body = result.model_dump()
            print(f"status: {resp.status}")
            print(f"response:")
            print(json.dumps(body, indent=2, ensure_ascii=False))
    except error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}")
        print(e.read().decode("utf-8", errors="ignore"))
    except error.URLError as e:
        print(f"URLError: {e.reason}")


def test_add(base_url: str, provider: str, model: str) -> None:
    print("=" * 40)
    print(f"测试: 上下文添加  [{provider} / {model}]")
    print("=" * 40)
    req = AddRequest(
        provider=provider,
        model=model,
        content="我喜欢用Python写代码，常用FastAPI框架",
        user_id="test_user",
        tag="preference",
    )
    send(f"{base_url}/context/add", req.model_dump(), AddResponse)


def test_search(base_url: str, provider: str, model: str) -> None:
    print("=" * 40)
    print(f"测试: 上下文搜索  [{provider} / {model}]")
    print("=" * 40)
    req = SearchRequest(
        provider=provider,
        model=model,
        query="我喜欢什么编程语言",
        user_id="test_user",
        tag="preference",
    )
    send(f"{base_url}/context/search", req.model_dump(), SearchResponse)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Context API 测试")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务器IP")
    parser.add_argument("--port", type=int, default=9999, help="服务器端口")
    parser.add_argument("--provider", type=str, default="mem0", help="提供商")
    parser.add_argument("--model", type=str, default="", help="模型")
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    test_add(base_url, args.provider, args.model)
    print()
    test_search(base_url, args.provider, args.model)
