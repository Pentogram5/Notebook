# http_client.py

import requests
import time

def test_http_delay(url):
    
    S = 0
    N = 100
    for i in range(N):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        elapsed_time = end_time - start_time
        # print(f'Response: {response.text}')
        # print(f'Time taken: {elapsed_time:.2f} seconds')
        val = elapsed_time
        S += val
    print(S/N)

if __name__ == '__main__':
    url = 'http://192.168.2.12:8080'  # Change this if your server runs on a different address/port
    test_http_delay(url)
