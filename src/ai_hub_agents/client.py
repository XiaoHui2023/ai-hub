import requests
from pathlib import Path
import mimetypes
from .app import ResponseModel

def post(url: str, thread_id: str, query: str, user_name: str, file_paths: list[str]=None) -> ResponseModel:
    """
    POST 请求
    Args:
        url: 请求 URL
        thread_id: 线程 ID
        query: 查询文本
        user_name: 用户名称
        file_paths: 文件路径列表
    Returns:
        ResponseModel: 响应数据
    """
    if file_paths is None:
        file_paths = []
    data = {"thread_id": thread_id, "query": query, "user_name": user_name}
    files = [
        ("files", (Path(file).name, open(file, "rb"), get_content_type(file)))
        for file in file_paths
    ]
    resp = requests.post(url, data=data, files=files)
    return ResponseModel.model_validate(resp.json())

def get_content_type(path: str) -> str:
    """
    Get the content type of a file
    Args:
        path: 文件路径
    Returns:
        str: 内容类型
    """
    return mimetypes.guess_type(path)[0] or "application/octet-stream"

__all__ = [
    "post",
]