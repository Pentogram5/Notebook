import asyncio
import aiohttp
import time
import threading

# SERVER_IP = "http://localhost:8080"

class TimeStamper:
    def __init__(self):
        self.old_t = time.time()

    def timestamp(self):
        dt = time.time() - self.old_t
        self.old_t = time.time()
        return dt

class RobotDirection:
    def __init__(self, ip="http://localhost:8080"):
        self.ip = ip
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.running = True

    async def send_request(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    def set_speed_cms_left(self, cms):
        url = f'{self.ip}/set_speed_cms_left?cms={cms}'
        # Запускаем асинхронную задачу
        self.loop.call_soon_threadsafe(asyncio.create_task, self.send_request(url))

    def set_speed_cms_right(self, cms):
        url = f'{self.ip}/set_speed_cms_right?cms={cms}'
        # Запускаем асинхронную задачу
        self.loop.call_soon_threadsafe(asyncio.create_task, self.send_request(url))

    def run(self):
        try:
            while self.running:
                # Позволяем циклу событий выполнять другие задачи
                self.loop.run_until_complete(asyncio.sleep(0))
        finally:
            self.loop.close()

# Пример использования
if __name__ == '__main__':
    ts = TimeStamper()
    motor_controller = RobotDirection()

    # Запускаем поток для обработки асинхронных задач
    thread = threading.Thread(target=motor_controller.run)
    thread.start()

    try:
        while True:
            motor_controller.set_speed_cms_left(10.5)
            # ts.timestamp()
            motor_controller.set_speed_cms_right(12.3)
            print(ts.timestamp())
            # time.sleep(1)  # Задержка для демонстрации
    except KeyboardInterrupt:
        motor_controller.running = False  # Останавливаем цикл при завершении
        thread.join()  # Ждем завершения потока
