import asyncio
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from collections import defaultdict
import uvicorn
from ai_hub_agents import settings
from pydantic import BaseModel, Field
from .callback import APIRequest, APIResponse, APIRoundtrip
from .renderers import AppServe
import logging

app = FastAPI()

logger = logging.getLogger(__name__)

# 每个 thread_id 一个锁
_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

class FilePart(BaseModel):
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="文件内容")
    type: str | None = Field(None, description="文件类型")

class ResponseModel(BaseModel):
    response: str = Field(..., description="响应文本")
    files: list[FilePart] = Field(default_factory=list, description="文件列表")

# 清理长期不用的 lock，避免内存泄漏
def _get_lock(thread_id: str) -> asyncio.Lock:
    lock = _locks[thread_id]
    return lock

@app.post("/",response_model=ResponseModel)
async def endpoint(
    thread_id: str = Form(..., description="对象+会话 ID"),
    query: str = Form(..., description="查询文本"),
    files: list[UploadFile] = File(default_factory=list, description="文件列表"),
    user_name: str|None = Form(None, description="用户名称"),
):
    lock = _get_lock(thread_id)
    queue_timeout = settings.app_queue_timeout
    exec_timeout = settings.app_exec_timeout

    try:
        # 排队：超时则放弃
        async with asyncio.timeout(queue_timeout):
            async with lock:
                # 进入锁后，用执行超时包裹实际逻辑
                async with asyncio.timeout(exec_timeout):
                    return await _do_work(query, thread_id, files, user_name)
    except asyncio.TimeoutError:
        logger.error(f"请求超时: {query}, {thread_id}, {files}, {user_name}")
        raise HTTPException(504, "请求超时")

async def _do_work(query: str, thread_id: str, files: list[UploadFile], user_name: str|None) -> APIResponse:
    """实际业务逻辑"""
    roundtrip = await APIRoundtrip.atrigger(
        request=APIRequest.trigger(
            query=query,
            thread_id=thread_id,
            files=files,
            user_name=user_name
        )
    )
    if not roundtrip.response:
        logger.error(f"未处理响应: {query}, {thread_id}, {files}, {user_name}")
        raise HTTPException(500, "未处理响应")
    return roundtrip.response

def run(host: str = None, port: int = None, reload: bool = None):
    """运行APP"""
    # 默认值
    host = host or settings.host
    port = port or settings.port
    reload = reload if reload is not None else settings.reload

    AppServe()
    
    uvicorn.run(
        "ai_hub_agents.app:app",           # 或 app
        host=host,      # 0.0.0.0 表示监听所有网卡
        port=port,
        reload=reload,         # 开发时热重载
    )

__all__ = [
    "run",
]