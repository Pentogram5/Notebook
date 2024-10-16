import asyncio
import aiohttp
import threading
import time
from SC_API_motors import RobotDirection
from SC_infrared import ScInfrared
from SC_ultrasonic import ScUltrasonic

# Глобальная переменная для IP адреса сервера
SERVER_IP = "http://localhost:8080"

# Глобальные объекты
IR_G = None
IR_R = None
IR_B = None
ULTRASONIC = None
MOTOR_CONTROLLER = None

class TimeStamper:
    def __init__(self):
        self.old_t = time.time()

    def timestamp(self):
        dt = time.time() - self.old_t
        self.old_t = time.time()
        return dt
    
ts = TimeStamper()

async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()  # Генерирует исключение для статусов 4xx/5xx
        return await response.json()

async def fetch_and_deserialize(url, class_type):
    global IR_G, IR_R, IR_B, ULTRASONIC
    
    async with aiohttp.ClientSession() as session:
        try:
            json_data = await fetch(session, url)
            obj = class_type.deserialize(json_data)

            # Присваиваем объект в зависимости от URL
            if url.endswith('/get_IR_G'):
                global IR_G
                IR_G = obj
            elif url.endswith('/get_IR_R'):
                global IR_R
                IR_R = obj
            elif url.endswith('/get_IR_B'):
                global IR_B
                IR_B = obj
            elif url.endswith('/get_ultrasonic_sensor'):
                global ULTRASONIC
                ULTRASONIC = obj

        except Exception as e:
            print(f"Error fetching data from {url}: {e}")

async def main():
    urls = [
        f"{SERVER_IP}/get_IR_G",
        f"{SERVER_IP}/get_IR_R",
        f"{SERVER_IP}/get_IR_B",
        f"{SERVER_IP}/get_ultrasonic_sensor"
    ]
    
    tasks = [
        fetch_and_deserialize(urls[0], ScInfrared),  # IR_G
        fetch_and_deserialize(urls[1], ScInfrared),  # IR_R
        fetch_and_deserialize(urls[2], ScInfrared),  # IR_B
        fetch_and_deserialize(urls[3], ScUltrasonic)  # ULTRASONIC
    ]

    await asyncio.gather(*tasks)

def start_callback_thread():
    global MOTOR_CONTROLLER
    loop = asyncio.new_event_loop()
    MOTOR_CONTROLLER = RobotDirection(ip=SERVER_IP, loop=loop)
    
    def run():
        asyncio.set_event_loop(loop)
        while True:
            loop.run_until_complete(main())
            time.sleep(0)  # Задержка между циклами

    thread = threading.Thread(target=run)
    thread.daemon = True  # Позволяет завершить поток при завершении основного потока
    thread.start()

if __name__ == "__main__":
    start_callback_thread()
    
    # Основной поток может выполнять другие задачи или просто ожидать завершения.
    try:
        while True:
            MOTOR_CONTROLLER.set_speed_cms_left(100)
            MOTOR_CONTROLLER.set_speed_cms_right(100)
            print(f"Elapsed time: {ts.timestamp()} seconds")
            time.sleep(0)  # Задержка для демонстрации
    except KeyboardInterrupt:
        print("Program terminated.")
