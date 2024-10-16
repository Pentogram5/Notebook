import socket
import json
import threading
import queue

class StableConnectionServer:
    def __init__(self, ip='127.0.0.1', port=5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        self.clients = []
        self.running = True

    def start_process_responses(self):
        threading.Thread(target=self._accept_clients, daemon=True).start()

    def _accept_clients(self):
        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Client connected: {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self._handle_client, args=(client_socket,), daemon=True).start()

    def _handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                json_request = json.loads(data.decode('utf-8'))
                json_response = self.process_response(json_request)
                client_socket.sendall(json.dumps(json_response).encode('utf-8'))
            except Exception as e:
                print(f"Error handling client: {e}")
                break
        client_socket.close()
        print("Client disconnected")

    def process_response(self, json_request):
        # Пользователь должен реализовать эту функцию
        raise NotImplementedError("process_response() must be implemented by the user")

    def stop(self):
        self.running = False
        self.server_socket.close()


class StableConnectionClient:
    def __init__(self, ip='127.0.0.1', port=5000, lock_policy='blocking'):
        self.server_address = (ip, port)
        self.lock_policy = lock_policy
        self.lock = threading.Lock()
        self.queue = queue.Queue()
        self.is_processing = False
        self.socket = None
        self.connect()

    def connect(self):
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect(self.server_address)
                print("Connected to server")
                break
            except ConnectionRefusedError:
                print("Connection failed, retrying...")
    
    def request(self, json_request: dict):
        if not isinstance(json_request, dict) or "request_name" not in json_request:
            raise ValueError("json_request must be a dictionary with at least 'request_name' key")

        if self.is_processing:
            if self.lock_policy == 'blocking':
                self.queue.put(json_request)
                return {"response_code": 202, "response_msg": "Request queued"}
            elif self.lock_policy == 'skipping':
                return {"response_code": 409, "response_msg": "Клиент не может отправить 2 сообщения параллельно. Дождитесь отправки старого"}

        return self._send_request(json_request)

    def _send_request(self, json_request):
        with self.lock:
            self.is_processing = True
            try:
                request_str = json.dumps(json_request)
                self.socket.sendall(request_str.encode('utf-8'))
                
                response_data = self.socket.recv(1024)
                json_response = json.loads(response_data.decode('utf-8'))
                
                return json_response
            finally:
                self.is_processing = False
            
            # Обработка очереди после завершения текущего запроса
            while not self.queue.empty():
                next_request = self.queue.get()
                response = self._send_request(next_request)
                if response is not None:
                    return response

    def close(self):
        if self.socket:
            self.socket.close()
