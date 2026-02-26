"""XlsxAgent HTTP 服务器。"""

import argparse

from ai_hub_agents.server import serve
from ai_hub_agents.test import load_test_llm, setup_logging
from ai_hub_agents.xlsx import XlsxAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="XlsxAgent HTTP 服务")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001, help="监听端口 (默认: 8001)")
    args = parser.parse_args()

    setup_logging()
    llm = load_test_llm()
    serve(XlsxAgent, llm, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
