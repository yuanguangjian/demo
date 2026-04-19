import aiohttp
import asyncio
import time

# URL = "http://localhost:8899/getUploadTask?uploadId=263D861AF710415A8A0DB11AF7E44DCA"
# URL = "http://localhost:8888/upload/getUploadTask?uploadId=263D861AF710415A8A0DB11AF7E44DCA"
# URL = "http://localhost:8888/upload/getUploadTask?uploadId=D3C8664C8FFC4B838B62755CE84C7A10"
URL = "http://192.168.75.132:8080/getKey?key=name&value=hello"

async def call_api(session, i):
    try:
        async with session.get(URL) as resp:
            return f"Task {i}: {resp.status}"
    except Exception as e:
        return f"Task {i}: error {e}"

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [call_api(session, i) for i in range(1000)]  # 1000 请求
        results = await asyncio.gather(*tasks)
        for r in results[:10]:
            print(r)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"Total time: {end - start:.2f}s")
