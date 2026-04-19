import aiohttp
import asyncio
import time

URL = "http://192.168.75.132:8080/getKey?key=name&value=hello"
# URL = "http://192.168.75.132:8899/"
DURATION = 30  # 持续 30 秒
CONCURRENCY = 2000  # 最大并发数

async def call_api(session, task_id):
    try:
        async with session.get(URL) as resp:
            return f"Task {task_id}: {resp.status}"
    except Exception as e:
        return f"Task {task_id}: error {e}"

async def worker(session, task_id_queue):
    while True:
        try:
            task_id = task_id_queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        await call_api(session, task_id)

async def main():
    start_time = time.time()
    task_id = 0
    tasks_done = 0

    # 使用信号量限制并发
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def limited_call():
        nonlocal task_id, tasks_done
        async with semaphore:
            tid = task_id
            task_id += 1
            result = await call_api(session, tid)
            tasks_done += 1
            if tid < 10:  # 打印前几个结果
                print(result)
            return result

    async with aiohttp.ClientSession() as session:
        # 持续创建任务，直到时间到
        pending = set()
        while time.time() - start_time < DURATION:
            # 启动一个新任务
            pending.add(asyncio.create_task(limited_call()))
            # 避免创建太快（可选）
            await asyncio.sleep(0)  # 让出控制权

        # 等待所有已启动的任务完成
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    print(f"Total time: {time.time() - start_time:.2f}s")
    print(f"Total requests sent: {task_id}")

if __name__ == "__main__":
    asyncio.run(main())