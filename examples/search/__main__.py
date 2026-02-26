import argparse

from ai_hub_agents.search import SearchAgent
from ai_hub_agents.test import ColorStreamRenderer, load_test_llm, setup_logging

DEFAULT_QUERY = "LangGraph 是什么？有哪些核心概念？"


def main() -> None:
    parser = argparse.ArgumentParser(description="SearchAgent - 搜索问答 CLI")
    parser.add_argument("-q", "--query", default=DEFAULT_QUERY, help="搜索问题")
    parser.add_argument("-p", "--provider", default=None, help="搜索 Provider")
    args = parser.parse_args()

    setup_logging()

    llm = load_test_llm()
    agent = SearchAgent.create(llm, provider_name=args.provider)

    print(f"搜索: {args.query}")
    result = agent.invoke(args.query, callbacks=[ColorStreamRenderer()])
    print(result)


if __name__ == "__main__":
    main()
