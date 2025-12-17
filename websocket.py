import asyncio
import websockets
import time
import argparse
import random
import logging
import signal
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("websocket_test.log")
    ]
)
logger = logging.getLogger(__name__)

# 全局变量
active_connections = 0
failed_connections = 0
connection_times = []
message_latencies = []
connections = []


async def connect_websocket(url, connection_id, message_interval, test_duration):
    """建立WebSocket连接并保持活跃"""
    global active_connections, failed_connections, connection_times

    start_time = time.time()
    try:
        # 尝试建立连接
        async with websockets.connect(url, ping_interval=20, ping_timeout=60, close_timeout=10) as websocket:
            conn_time = time.time() - start_time
            connection_times.append(conn_time)

            # 连接成功，递增活跃连接计数
            active_connections += 1
            logger.debug(f"连接 #{connection_id} 已建立，耗时: {conn_time:.4f}秒")

            # 保持连接并定期发送消息
            end_time = start_time + test_duration
            while time.time() < end_time:
                try:
                    # 发送消息并测量延迟
                    msg_send_time = time.time()
                    message = f"The sky is blue today. I love watching clouds drift by slowly. Coffee tastes best in the morning. Books open new worlds to explore. Music soothes the troubled mind. Walking daily improves health. Friends gather to share stories. Time passes quickly when busy. Dogs make loyal companions. Cats sleep most of the day. Rain taps gently on windows. Snow covers the ground in white. Trees sway in the gentle breeze. Stars twinkle in the night sky. Oceans contain countless mysteries. Mountains reach toward heaven. Flowers bloom in the spring. Birds sing sweet melodies. Children laugh while playing. Teachers inspire young minds. Artists create beautiful works. Writers capture human experience. Scientists discover new facts. Doctors heal the sick. Farmers grow our food. Bakers make delicious bread. Chefs create amazing dishes. Dancers move with grace. Singers touch our hearts. Actors bring stories to life. Movies transport us elsewhere. Books contain endless wisdom. Computers connect the world. Phones keep people in touch. Cars take us to new places. Trains run on schedule. Planes fly through the sky. Boats sail across waters. Bicycles provide exercise. Walking costs nothing. Running builds endurance. Swimming cools hot bodies. Hiking explores nature. Camping connects to earth. Fishing requires patience. #{connection_id}-{random.randint(1, 10000)}"
                    await websocket.send(message)

                    # 等待服务器响应
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    latency = time.time() - msg_send_time
                    message_latencies.append(latency)

                    logger.debug(f"连接 #{connection_id} 消息延迟: {latency:.4f}秒")

                    # 随机等待指定时间间隔
                    await asyncio.sleep(message_interval * (0.8 + 0.4 * random.random()))
                except asyncio.TimeoutError:
                    logger.warning(f"连接 #{connection_id} 消息超时")
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"连接 #{connection_id} 已被服务器关闭")
                    active_connections -= 1
                    failed_connections += 1
                    return

    except (websockets.exceptions.WebSocketException, ConnectionRefusedError, OSError) as e:
        failed_connections += 1
        logger.error(f"连接 #{connection_id} 建立失败: {str(e)}")


async def connection_monitor():
    """监控并显示当前连接状态"""
    last_count = 0
    while True:
        await asyncio.sleep(1)
        current = active_connections
        if current != last_count:
            logger.info(f"当前活跃连接数: {current}, 失败连接: {failed_connections}")
            last_count = current


async def create_connections(url, num_connections, ramp_up, message_interval, test_duration):
    """创建指定数量的WebSocket连接"""
    logger.info(f"开始测试: 目标 {num_connections} 个连接, 每个持续 {test_duration} 秒")

    # 启动连接监控器
    asyncio.create_task(connection_monitor())

    # 计算连接之间的延迟（分散创建连接）
    delay_between_conn = ramp_up / num_connections if num_connections > 0 else 0

    # 创建多个连接任务
    tasks = []
    for i in range(num_connections):
        # 添加一点随机性，避免完全同步创建连接
        delay = delay_between_conn * i * (0.9 + 0.2 * random.random())

        # 创建延迟任务
        task = asyncio.create_task(
            delayed_connect(url, i + 1, delay, message_interval, test_duration)
        )
        tasks.append(task)

    # 等待所有连接任务完成
    await asyncio.gather(*tasks)

    # 输出测试结果
    print_test_results(num_connections, test_duration)


async def delayed_connect(url, connection_id, delay, message_interval, test_duration):
    """延迟一段时间后创建连接"""
    await asyncio.sleep(delay)
    await connect_websocket(url, connection_id, message_interval, test_duration)


def print_test_results(num_connections, test_duration):
    """打印测试结果统计"""
    logger.info("=" * 50)
    logger.info("WebSocket连接测试结果")
    logger.info("=" * 50)
    logger.info(f"目标连接数: {num_connections}")
    logger.info(f"成功建立连接: {active_connections + failed_connections - failed_connections}")
    logger.info(f"失败连接: {failed_connections}")
    logger.info(f"测试持续时间: {test_duration} 秒")

    if connection_times:
        logger.info(f"平均连接时间: {sum(connection_times) / len(connection_times):.4f} 秒")
        logger.info(f"最长连接时间: {max(connection_times):.4f} 秒")
        logger.info(f"最短连接时间: {min(connection_times):.4f} 秒")

    if message_latencies:
        logger.info(f"平均消息延迟: {sum(message_latencies) / len(message_latencies):.4f} 秒")
        logger.info(f"最长消息延迟: {max(message_latencies):.4f} 秒")
        logger.info(f"最短消息延迟: {min(message_latencies):.4f} 秒")

    logger.info("=" * 50)


def handle_signal(sig, frame):
    """处理程序中断信号"""
    logger.info("接收到中断信号，正在停止测试...")
    # 输出当前测试结果
    print_test_results(0, 0)
    sys.exit(0)


async def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="WebSocket连接负载测试工具")
    parser.add_argument("url", help="WebSocket服务器URL (ws://... 或 wss://...)")
    parser.add_argument("-n", "--connections", type=int, default=2000, help="要创建的连接数量 (默认: 100)")
    parser.add_argument("-r", "--ramp-up", type=float, default=30.0, help="连接爬升时间(秒) (默认: 30秒)")
    parser.add_argument("-d", "--duration", type=float, default=60.0, help="测试持续时间(秒) (默认: 60秒)")
    parser.add_argument("-i", "--interval", type=float, default=5.0, help="消息发送间隔(秒) (默认: 5秒)")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志")

    args = parser.parse_args()

    # 设置详细日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # 执行连接测试
    await create_connections(
        args.url,
        args.connections,
        args.ramp_up,
        args.interval,
        args.duration
    )


if __name__ == "__main__":
    # 设置更大的连接池
    asyncio.run(main(), debug=False)