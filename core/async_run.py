import asyncio
import threading
from typing import Callable
from concurrent.futures import Future
from typing import Dict, Tuple, AsyncGenerator, Awaitable

def async_run(func: Callable, *args, **kwargs) -> Future:
    '''
    异步运行异步函数并返回 Future 对象
    '''
    future = Future()
    
    def run_loop():
        try:  # 整个 run_loop 都要包在 try-catch 中
            if asyncio.iscoroutinefunction(func):
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(func(*args, **kwargs))
                    future.set_result(result)
                except Exception as e:
                    # 打印完整的traceback到控制台
                    future.set_exception(e)
                finally:
                    loop.close()
            else:
                # 同步函数也要包在 try-catch 中
                result = func(*args, **kwargs)
                future.set_result(result)
        except Exception as e:  # 捕获所有异常
            # 打印完整的traceback到控制台
            future.set_exception(e)
    
    thread = threading.Thread(target=run_loop)
    thread.start()
    return future

async def run_generators(generator_map:Dict[str,AsyncGenerator]) -> AsyncGenerator[Tuple[str,any],None]:
    if not generator_map:
        return

    queue = asyncio.Queue()

    generators = list(generator_map.values())
    name_map = {generator:name for name,generator in generator_map.items()}

    async def process_generator(gen):
        async for item in gen:
            if item is not None:
                name = name_map[gen]
                await queue.put((name,item))

    # 启动所有生成器
    tasks = [
        asyncio.create_task(process_generator(gen))
        for gen in generators
    ]
    
    # 等待所有生成器完成
    gen_task = asyncio.gather(*tasks)
    get_task = None
    while True:
        if get_task is None:
            get_task = asyncio.create_task(queue.get())
        tasks = [get_task, gen_task]
        # 等待 queue.get() 或 gather_task 完成
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        if any(isinstance(task, asyncio.Future) and task.done() for task in done):
            for task in done:
                if task is not gen_task:
                    result = task.result()
                    yield result

        if gen_task in done:
            # 所有生成器都结束了，queue 里可能还有剩余数据
            while not queue.empty():
                result = queue.get_nowait()
                yield result
            break
        
        if get_task in done:
            get_task = None
    
    for task in tasks:
        if task is not None:
            task.cancel()
            pass

async def run_async(func:Awaitable,*args,**kwargs) -> any:
    '''
    运行异步函数
    '''
    item = ""

    async def generator():
        rt = await func(*args,**kwargs)
        yield rt
    async for _,item in run_generators({"":generator()}):
        pass

    return item