"""QaAgent HTTP 服务器。"""

import argparse

from ai_hub_agents.qa import QaAgent
from ai_hub_agents.server import serve
from ai_hub_agents.test import load_test_llm, setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="QaAgent HTTP 服务")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8004, help="监听端口 (默认: 8004)")
    parser.add_argument("--provider", default=None, help="搜索 Provider 名称")
    args = parser.parse_args()

    setup_logging()
    llm = load_test_llm()
    serve(QaAgent, llm, host=args.host, port=args.port, provider_name=args.provider)


if __name__ == "__main__":
    main()
