import json
import time
from SC_TCPRequests import StableConnectionClient

if __name__ == "__main__":
    client = StableConnectionClient(ip='127.0.0.1', port=5000, lock_policy='blocking')
    
    try:
        while True:
            # Отправляем запрос каждые 5 секунд
            request = {"request_name": "World"}
            response = client.request(request)
            print(f"Response: {response}")
            # time.sleep(5)  # Ждем перед отправкой следующего запроса
    except KeyboardInterrupt:
        print("Stopping client...")
        client.close()
