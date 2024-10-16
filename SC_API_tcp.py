import socket
import json
import threading
import time

from SC_infrared import ScInfrared
from SC_ultrasonic import ScUltrasonic

SERVER_IP = 'localhost'
PORT_SENSOR = 8081
PORT_COMMAND = 8082
PORT_ACTION = 8083  # Новый порт для действий
UPDATE_RATE = 30  # Частота в Гц

global IR_G, IR_R, IR_B, ULTRASONIC
IR_G, IR_R, IR_B, ULTRASONIC = ScInfrared(), ScInfrared(), ScInfrared(), ScUltrasonic()
class RobotDirection:
    def __init__(self):
        self.left_cms  = 0
        self.right_cms = 0
    def set_speed_cms_left (self, speed):
        self.left_cms = speed
    def set_speed_cms_right(self, speed):
        self.right_cms = speed
global rb
rb = RobotDirection()

# Глобальные переменные для скорости моторов
left_cms = 0
right_cms = 0

# Глобальные сокет-соединения
command_socket = None
action_socket = None

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

def parse_json_from_buffer(buffer):
    json_objects = []
    last_valid_json = None  # Keep track of the last valid JSON object
    start_index = 0  # Initialize the starting index for searching

    while True:
        try:
            # Find the next opening brace
            start_index = buffer.index('{', start_index)
            open_braces = 1  # Counter for nested braces
            
            # Find the corresponding closing brace
            end_index = start_index + 1
            while open_braces > 0 and end_index < len(buffer):
                if buffer[end_index] == '{':
                    open_braces += 1
                elif buffer[end_index] == '}':
                    open_braces -= 1
                end_index += 1
            
            # If we found a complete object, extract it
            if open_braces == 0:
                json_str = buffer[start_index:end_index]  # Extract complete JSON string
                json_objects.append(json.loads(json_str))  # Parse and append to the list
                last_valid_json = json.loads(json_str)  # Update last valid JSON
                
                # Move the starting index past this object for further searching
                start_index = end_index
            else:
                break  # Exit if we didn't find a complete object
            
        except (ValueError, json.JSONDecodeError):
            # If we can't find another opening brace or if there's an error in decoding, break out of the loop
            break

    return last_valid_json  # Return parsed objects, remaining buffer, and last valid JSON

def init_client():
    global command_socket, action_socket
    # Устанавливаем соединения один раз при запуске.
    
    command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reconnect_command_socket()
    
    action_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reconnect_action_socket()
    
    threading.Thread(target=receive_sensor_data).start()
    
    # Запускаем отправку команд в отдельном потоке
    threading.Thread(target=send_motor_commands).start()

def receive_sensor_data():
    buffer = ""
    rate_limiter = ThreadRate(UPDATE_RATE)
    
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_IP, PORT_SENSOR))
                while True:
                    data = s.recv(1024).decode('utf-8')
                    buffer += data
                    
                    # Пытаемся распарсить полные JSON-объекты из буфера
                    while True:
                        try:
                            sensor_data = parse_json_from_buffer(buffer)
                            # print(buffer, '|||| NIGGER ||||', sensor_data)
                            if sensor_data is None: break
                            buffer = ""
                            global IR_G, IR_R, IR_B, ULTRASONIC
                            IR_G = ScInfrared.deserialize(sensor_data['IR_G'])
                            IR_R = ScInfrared.deserialize(sensor_data['IR_R'])
                            IR_B = ScInfrared.deserialize(sensor_data['IR_B'])
                            ULTRASONIC =ScUltrasonic.deserialize(sensor_data['ULTRASONIC'])
                            break  # Выходим из внутреннего цикла для продолжения получения данных
                        except:
                            break
                    
                    rate_limiter.sleep()  # Сохраняем фиксированную частоту обновления

        except (ConnectionRefusedError, ConnectionResetError):
            print("Failed to connect to sensor server. Retrying in 5 seconds...")
            time.sleep(5)  # Ждем перед повторной попыткой подключения

def send_motor_commands():
    global left_cms, right_cms
    
    rate_limiter = ThreadRate(UPDATE_RATE)

    global command_socket
    
    while True:
        # print(left_cms, right_cms)
        try:
            command_socket.sendall(json.dumps({
                "set_speed": {
                    "left": left_cms,
                    "right": right_cms,
                }
            }).encode('utf-8'))
            
            rate_limiter.sleep()  # Сохраняем фиксированную частоту обновления
                
        except (ConnectionResetError):
            print("Motor command connection lost. Attempting to reconnect...")
            reconnect_command_socket()

def reconnect_command_socket():
    global command_socket
    
    while True:
        try:
            if command_socket: 
                command_socket.close() 
            
            command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            command_socket.connect((SERVER_IP, PORT_COMMAND))
            
            print("Reconnected to command server.")
            break
            
        except (ConnectionRefusedError, ConnectionResetError):
            print("Failed to connect to command server. Retrying in 5 seconds...")
            time.sleep(5)

def send_action(action):
    try:
        action_socket.sendall(json.dumps({"action": action}).encode('utf-8'))
            
    except (ConnectionResetError) as e:
        print(f"Failed to send action command: {action}. Error: {e}. Reconnecting...")
        reconnect_action_socket()

def reconnect_action_socket():
    global action_socket
    
    while True:
        try:
            if action_socket: 
                action_socket.close() 
            
            action_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            action_socket.connect((SERVER_IP, PORT_ACTION))
            
            print("Reconnected to action server.")
            break
            
        except (ConnectionRefusedError, ConnectionResetError):
            print("Failed to connect to action server. Retrying in 5 seconds...")
            time.sleep(5)



def main():
    init_client()
    
    tr = ThreadRate(30)
    ts = TimeStamper()
    old_ts = 0
    try:
        while True:
            rb.set_speed_cms_left(100)  # Пример значения для левого мотора
            rb.set_speed_cms_right(100)  # Пример значения для правого мотора
            
            send_action("perform_look_forward")   # Отправляем пример действия

            ts = IR_G.timestamp
            print(ts-old_ts)
            old_ts = IR_G.timestamp
            # print(ts.timestamp())
            
            tr.sleep()
            
            # time.sleep(1)  # Задержка для демонстрации (можно настроить по необходимости)
            
    except KeyboardInterrupt:
        print("Program terminated.")

if __name__ == "__main__":
    main()
