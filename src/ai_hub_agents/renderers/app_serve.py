from ai_hub_agents.callback import APIResponse, APIRoundtrip
from ai_hub_agents import Agent

class AppServe:
    def __init__(self):
        @APIRoundtrip
        async def _(cb: APIRoundtrip):
            if cb.request.files:
                raise NotImplementedError("文件上传功能未实现")
            response = await Agent(thread_id=cb.request.thread_id).run(cb.request.query)
            cb.response = APIResponse.trigger(
                thread_id=cb.request.thread_id,
                response=response,
                files=[], # 尚未实现
            )