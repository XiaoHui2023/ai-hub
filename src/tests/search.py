import json
import argparse
from urllib import request, error


def build_request(url: str, payload: dict) -> request.Request:
    return request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def send(url: str, payload: dict) -> None:
    """发送请求并打印结果"""
    req = build_request(url, payload)
    try:
        with request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="ignore"))
            print(f"status: {resp.status}")
            print(f"response:")
            print(json.dumps(body, indent=2, ensure_ascii=False))
    except error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}")
        print(e.read().decode("utf-8", errors="ignore"))
    except error.URLError as e:
        print(f"URLError: {e.reason}")


def test_search(url: str, provider: str, model: str, query: str) -> None:
    print("=" * 40)
    print(f"测试: 搜索  [{provider} / {model}]")
    print(f"查询: {query}")
    print("=" * 40)
    send(url, {
        "provider": provider,
        "model": model,
        "query": query,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search API 测试")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务器IP")
    parser.add_argument("--port", type=int, default=9999, help="服务器端口")
    parser.add_argument("--provider", type=str, default="bocha", help="提供商")
    parser.add_argument("--model", type=str, default="web-search", help="模型")
    parser.add_argument("--query", type=str, default="2026年Python最新的Web框架有哪些", help="搜索内容")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}/search/query"

    test_search(url, args.provider, args.model, args.query)