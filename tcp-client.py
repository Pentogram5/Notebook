import socket
import time

def test_tcp_delay(host='192.168.2.12', port=8080):
    S = 0
    N = 100
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        
        for i in range(N):
            start_time = time.time()
            message = f'Test message {i}'
            client_socket.sendall(message.encode())
            response = client_socket.recv(1024)
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            S += elapsed_time
            print(f'Time taken for round trip {i}: {elapsed_time:.6f} seconds')

    print(f'Average delay: {S/N:.6f} seconds')

if __name__ == '__main__':
    host = '192.168.2.12'  # Change this if your server runs on a different address
    test_tcp_delay(host)
