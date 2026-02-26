import argparse
import uuid

from ai_hub_agents.qa import QaAgent
from ai_hub_agents.test import ColorStreamRenderer,SqliteDebugRenderer, load_test_llm, setup_logging

DEFAULT_MESSAGE = "2026年有哪些值得关注的AI开源项目？"


def main() -> None:
    parser = argparse.ArgumentParser(description="QaAgent - 智能问答 CLI")
    parser.add_argument("-m", "--message", default=DEFAULT_MESSAGE, help="问题")
    parser.add_argument("-p", "--provider", default=None, help="搜索 Provider")
    parser.add_argument("--interactive", action="store_true", help="交互式模式")
    args = parser.parse_args()

    setup_logging()

    llm = load_test_llm()
    renderers = [ColorStreamRenderer(),SqliteDebugRenderer()]
    agent = QaAgent.create(llm, provider_name=args.provider, callbacks=renderers)
    thread_id = str(uuid.uuid4())

    if args.interactive:
        print("交互式问答模式（输入 exit 退出）")
        while True:
            user_input = input("\n你: ").strip()
            if user_input.lower() == "exit":
                break
            if not user_input:
                continue
            result = agent.invoke(user_input, thread_id=thread_id, callbacks=renderers)
            print(f"\n助手: {result}")
    else:
        print(f"问题: {args.message}")
        result = agent.invoke(args.message, thread_id=thread_id, callbacks=renderers)
        print(result)


if __name__ == "__main__":
    main()
