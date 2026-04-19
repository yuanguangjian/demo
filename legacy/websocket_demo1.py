import asyncio
import websockets
import logging
import signal
import sys

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 全局变量来跟踪活动连接
active_connections = set()
close_event = asyncio.Event()

# 异步函数来关闭所有活动连接
async def close_all_connections():
    logging.info("Closing all connections...")
    for ws in active_connections:
        try:
            await ws.close()
        except Exception as e:
            logging.error(f"Failed to close connection: {e}")
    active_connections.clear()
    logging.info("All connections closed.")

# 异步函数来创建和保持 WebSocket 连接
async def create_and_keep_websocket_connection(uri, connection_id):
    try:
        async with websockets.connect(uri) as websocket:
            logging.info(f"Connection {connection_id} established")
            active_connections.add(websocket)
            # 等待关闭事件
            await close_event.wait()
            logging.info(f"Connection {connection_id} is being closed due to close event")
            active_connections.discard(websocket)
            # 这里其实不需要再次调用 await ws.close()，因为连接已经在上面的 with 语句中关闭了
    except Exception as e:
        logging.error(f"Failed to establish or maintain connection {connection_id}: {e}")

# 主函数
async def main(uri, total_connections):
    # 创建并启动所有 WebSocket 连接任务
    tasks = [create_and_keep_websocket_connection(uri, i) for i in range(total_connections)]

    # 设置信号处理器来设置关闭事件
    def handle_exit_signal(signum, frame):
        logging.info(f"Received exit signal {signum}, scheduling connection closure...")
        close_event.set()  # 设置关闭事件，这将触发所有连接关闭
        # 注意：我们不在这里调用 asyncio.get_running_loop().stop()，因为那会导致事件循环立即停止，
        # 而我们还需要等待所有连接关闭任务完成。相反，我们将允许事件循环继续运行，直到所有任务自然结束。

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, handle_exit_signal)

    # 等待所有连接任务完成（实际上，由于 close_event.wait()，它们将永远不会真正完成，直到我们手动触发关闭）
    # 但是，由于我们设置了关闭事件并且不再需要等待它们实际完成（因为我们知道它们会在关闭事件被设置时退出），
    # 我们可以使用 asyncio.gather() 的 return_exceptions=True 参数来避免在连接关闭时抛出的异常中断整个程序。
    # 然而，在这个特定的例子中，由于我们在 with 语句中处理了连接关闭，并且没有在 gather 调用中处理异常，
    # 所以实际上我们不需要 return_exceptions=True，因为异常已经被日志记录了。但为了清晰起见，我还是会保留这个注释。
    await asyncio.gather(*tasks, return_exceptions=True)

# 运行主函数
if __name__ == "__main__":
    websocket_uri = "ws://localhost:8080/ws/xx"
    total_connections = 1000  # 注意：这可能会消耗大量资源，确保你的服务器能够处理

    try:
        asyncio.run(main(websocket_uri, total_connections))
    except KeyboardInterrupt:
        # 捕获 Ctrl+C 以触发退出信号处理器（实际上，由于我们已经设置了信号处理器，这一步可能是多余的，
        # 因为 Ctrl+C 会触发 SIGINT，而我们已经为 SIGINT 设置了处理器。但保留这个异常捕获可以作为一种安全措施。）
        pass
