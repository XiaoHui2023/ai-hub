import asyncio
from ai_hub_agents.core import setup_log
from ai_hub_agents import settings
from ai_hub_agents.core.agent import Agent
from ai_hub_agents.renderers import EventMonitor

async def main():
    """主函数"""
    setup_log(settings.log_dir, settings.log_level)
    EventMonitor()
    agent = Agent(thread_id="example-chat")
    response = await agent.run(query="给我讲一个冷笑话",user_name="user")
    response = await agent.run(query="今天是星期几",user_name="hacker")
    response = await agent.run(query="我说的上一句话是什么",user_name="user")
    response = await agent.run(query="我说的上一句话是什么",user_name="hacker")

if __name__ == "__main__":
    asyncio.run(main())