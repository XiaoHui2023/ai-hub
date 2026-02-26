import argparse
import uuid

from ai_hub_agents.chat import ChatAgent
from ai_hub_agents.test import ColorStreamRenderer, SqliteDebugRenderer, load_test_llm, setup_logging

DEFAULT_MESSAGE = "你怎么看待AI发展对人类的影响？"


def main() -> None:
    parser = argparse.ArgumentParser(description="ChatAgent - 对话 CLI")
    parser.add_argument("-m", "--message", default=DEFAULT_MESSAGE, help="消息")
    parser.add_argument("-i","--interactive", action="store_true", help="交互式模式")
    args = parser.parse_args()

    setup_logging()

    llm = load_test_llm()
    renderers = [
        ColorStreamRenderer(),
        SqliteDebugRenderer(),
    ]
    agent = ChatAgent.create(llm, callbacks=renderers)
    thread_id = str(uuid.uuid4())

    if args.interactive:
        print("交互式对话模式（输入 exit 退出）")
        while True:
            user_input = input("\n你: ").strip()
            if user_input.lower() == "exit":
                break
            if not user_input:
                continue
            result = agent.invoke(user_input, thread_id=thread_id, callbacks=renderers)
            print(f"\n助手: {result}")
    else:
        print(f"消息: {args.message}")
        result = agent.invoke(args.message, thread_id=thread_id, callbacks=renderers)
        print(result)


if __name__ == "__main__":
    main()
