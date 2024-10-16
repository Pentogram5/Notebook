import json
import threading
import time
from SC_TCPRequests import StableConnectionClient
from SC_infrared import ScInfrared
from SC_ultrasonic import ScUltrasonic

SERVER_IP = '192.168.2.12'
PORT_SENSOR = 8081
PORT_COMMAND = 8082
PORT_ACTION = 8083
UPDATE_RATE = 30  # Частота в Гц

global IR_G, IR_R, IR_B, ULTRASONIC
IR_G, IR_R, IR_B, ULTRASONIC = ScInfrared(), ScInfrared(), ScInfrared(), ScUltrasonic()

class RobotDirection:
    def __init__(self):
        self.left_cms = 0
        self.right_cms = 0
    
    def set_speed_cms_left(self, speed):
        self.left_cms = speed
    
    def set_speed_cms_right(self, speed):
        self.right_cms = speed

global rb
rb = RobotDirection()

# Глобальные клиенты
sensor_client = None
command_client = None
action_client = None

class TimeStamper:
    def __init__(self):
        self.old_t = time.time()

    def timestamp(self):
        dt = time.time() - self.old_t
        self.old_t = time.time()
        return dt

class ThreadRate:
    """Утилита для сна с фиксированной частотой."""
    def __init__(self, freq=1):
        self.freq = freq
        self._period = 1 / self.freq
        self.ts = TimeStamper()

    def sleep(self):
        sleep_time = max(self._period - self.ts.timestamp(), 0)
        time.sleep(sleep_time)

def init_clients():
    global sensor_client, command_client, action_client
    
    sensor_client = StableConnectionClient(ip=SERVER_IP, port=PORT_SENSOR)
    command_client = StableConnectionClient(ip=SERVER_IP, port=PORT_COMMAND)
    action_client = StableConnectionClient(ip=SERVER_IP, port=PORT_ACTION)
    
    # Запускаем потоки для получения данных сенсоров и отправки команд моторам
    threading.Thread(target=receive_sensor_data, daemon=True).start()
    threading.Thread(target=send_motor_commands, daemon=True).start()

def get_constants():
    global IR_G, IR_R, IR_B, ULTRASONIC
    return IR_G, IR_R, IR_B, ULTRASONIC
    
def receive_sensor_data():
    global IR_G, IR_R, IR_B, ULTRASONIC
    rate_limiter = ThreadRate(UPDATE_RATE)
    
    while True:
        try:
            response = sensor_client.request({"request_name": "get_sensors"})
            # print(response)
            if response and response.get("response_code") == 200:
                # Обновляем значения сенсоров
                IR_G = ScInfrared.deserialize(response['sensors']['IR_G'])
                IR_R = ScInfrared.deserialize(response['sensors']['IR_R'])
                IR_B = ScInfrared.deserialize(response['sensors']['IR_B'])
                ULTRASONIC = ScUltrasonic.deserialize(response['sensors']['ULTRASONIC'])
                # print('A',IR_B)
            else:
                print("Failed to get sensor data:", response)
                
            rate_limiter.sleep()  # Задержка для поддержания частоты обновления
            
        except Exception as e:
            print(f"Error receiving sensor data: {e}")
            time.sleep(5)  # Ждем перед повторной попыткой подключения

def send_motor_commands():
    rate_limiter = ThreadRate(UPDATE_RATE)

    while True:
        try:
            command_response = command_client.request({
                "request_name": "set_speed_cms",
                "lcms": rb.left_cms,
                "rcms": rb.right_cms,
            })
            if command_response and command_response.get("response_code") != 200:
                print("Failed to set motor speed:", command_response)
                
            rate_limiter.sleep()  # Задержка для поддержания частоты обновления
                
        except Exception as e:
            print(f"Error sending motor commands: {e}")
            time.sleep(5)  # Ждем перед повторной попыткой подключения

def send_action(action):
    try:
        action_response = action_client.request({
            "request_name": "perform_action",
            "atype": action,
        })
        if action_response and action_response.get("response_code") != 200:
            print("Failed to perform action:", action_response)
            
    except Exception as e:
        print(f"Failed to send action command: {action}. Error: {e}")

def perform_action_capture():
    send_action("perform_action_capture")

def perform_action_throw_to_basket():
    send_action("perform_action_throw_to_basket")

ts = TimeStamper()
def main():
    init_clients()

    rate_limiter_action = ThreadRate(UPDATE_RATE)  # Для управления частотой действий
    old_tss = 0
    try:
        while True:
            # a, b = list(map(int,input().split(' ')))
            # print(a, b)
            # rb.set_speed_cms_left(a)  # Пример значения для левого мотора
            # rb.set_speed_cms_right(b)  # Пример значения для правого мотора
            # print('AAA')
            # send_action("perform_look_forward")   # Отправляем пример действия
            
            # tss = IR_G.timestamp
            # # print(ts.timestamp(), tss-old_tss)
            # old_tss = tss
            # print(IR_B)
            # print(ULTRASONIC)
            a = input()
            if a=='1':
                perform_action_capture()
            if a=='2':
                perform_action_throw_to_basket()
            
            # rate_limiter_action.sleep()  # Задержка для поддержания частоты обновления действий
            
    except KeyboardInterrupt:
        print("Program terminated.")

if __name__ == "__main__":
    main()
