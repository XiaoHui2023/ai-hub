@app.post("/api/xlsx/process")
async def process(file_id: str, task: str):
    renderer = SSEStreamRenderer()

    async def run_agent():
        agent.invoke(task, callbacks=[renderer], input_file=..., output_file=...)

    async def event_stream():
        task_future = asyncio.get_event_loop().run_in_executor(None, run_agent_sync)
        while True:
            try:
                data = await asyncio.wait_for(renderer.queue.get(), timeout=0.5)
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                if task_future.done():
                    break
        # 发送下载链接
        yield f"data: {json.dumps({'type': 'done', 'download_url': f'/api/xlsx/download/{result_id}'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")