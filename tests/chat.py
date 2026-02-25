import json
import argparse
from urllib import request, error

import ai_hub_protocol as protocol

MESSAGES = [
    protocol.chat.completion.Message(role="system", content="你是一个乐于助人的中文助手。"),
    protocol.chat.completion.Message(role="user", content="你好，帮我写一段早安问候。"),
]


def build_request(url: str, payload: dict) -> request.Request:
    return request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def send(url: str, payload: dict) -> None:
    """非流式：等待完整响应后打印"""
    req = build_request(url, payload)
    try:
        with request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="ignore"))
            result = protocol.chat.completion.Response.model_validate(body)
            print(f"status: {resp.status}")
            print(f"response:\n{result.content}")
    except error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}")
        print(e.read().decode("utf-8", errors="ignore"))
    except error.URLError as e:
        print(f"URLError: {e.reason}")


def send_stream(url: str, payload: dict) -> None:
    """流式：按 SSE 格式逐行读取并即时打印"""
    req = build_request(url, payload)
    try:
        with request.urlopen(req, timeout=60) as resp:
            print(f"status: {resp.status}")
            print("response:")
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "content" in data:
                        chunk = protocol.chat.completion.Response.model_validate(data)
                        print(chunk.content, end="", flush=True)
                    elif "error" in data:
                        print(f"\nerror: {data['error']}")
            print()
    except error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}")
        print(e.read().decode("utf-8", errors="ignore"))
    except error.URLError as e:
        print(f"URLError: {e.reason}")


def test_normal(url: str, provider: str, model: str) -> None:
    print("=" * 40)
    print(f"测试: 非流式传输  [{provider} / {model}]")
    print("=" * 40)
    req = protocol.chat.completion.Request(
        provider=provider, model=model, stream=False, messages=MESSAGES,
    )
    send(url, req.model_dump())


def test_stream(url: str, provider: str, model: str) -> None:
    print("=" * 40)
    print(f"测试: 流式传输  [{provider} / {model}]")
    print("=" * 40)
    req = protocol.chat.completion.Request(
        provider=provider, model=model, stream=True, messages=MESSAGES,
    )
    send_stream(url, req.model_dump())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat API 测试")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务器IP")
    parser.add_argument("--port", type=int, default=9999, help="服务器端口")
    parser.add_argument("--provider", type=str, help="提供商")
    parser.add_argument("--model", type=str, help="模型")
    args = parser.parse_args()

    provider = args.provider
    model = args.model
    url = f"http://{args.host}:{args.port}/chat/completion"

    test_normal(url, provider, model)
    print()
    test_stream(url, provider, model)
