import argparse
import os

from pathlib import Path
from ai_hub_agents.test import ColorStreamRenderer, load_test_llm, setup_logging
from ai_hub_agents.xlsx import XlsxAgent

PROJECT_ROOT = Path(__file__).resolve().parent

DEFAULT_INPUT_FILE = PROJECT_ROOT / "example.xlsx"
DEFAULT_OUTPUT_FILE = Path("output") / "example-result.xlsx"
DEFAULT_TASK = "帮我把所有没被退货的商品的行用绿色背景标出，退货最多的用红色标出；计算人数、次数、销售额等的总和"


def main() -> None:
    parser = argparse.ArgumentParser(description="XlsxAgent - Excel 处理 CLI")
    parser.add_argument("-i", "--input_file", default=DEFAULT_INPUT_FILE, help="输入 Excel 文件路径")
    parser.add_argument("-o", "--output_file", default=DEFAULT_OUTPUT_FILE, help="输出 Excel 文件路径")
    parser.add_argument("-t", "--task", default=DEFAULT_TASK, help="任务描述")
    args = parser.parse_args()

    setup_logging()

    input_file = os.path.abspath(args.input_file)
    output_file = os.path.abspath(args.output_file)

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"错误: 输入文件不存在 {input_file}")

    llm = load_test_llm()
    agent = XlsxAgent.create(llm)

    task = args.task

    print(f"输入: {input_file}")
    print(f"输出: {output_file}")
    print(f"任务: {task}")

    state_fields = dict(input_file=input_file, output_file=output_file)

    result = agent.invoke(task, callbacks=[ColorStreamRenderer()], **state_fields)
    print(result)


if __name__ == "__main__":
    main()
