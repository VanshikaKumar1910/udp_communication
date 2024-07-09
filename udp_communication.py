import socket
import struct
import threading
import time

def get_host_port():
    host = input("Enter the host IP (e.g., 127.0.0.1 for localhost): ")
    while True:
        try:
            port = int(input("Enter the port number (1024-65535): "))
            if 1024 <= port <= 65535:
                return host, port
            else:
                print("Port must be between 1024 and 65535.")
        except ValueError:
            print("Please enter a valid integer for the port.")

def send_data(sock, host, port):
    data_types = {
        '1': ('int', 'i'),
        '2': ('float', 'f'),
        '3': ('unsigned int', 'I'),
        '4': ('char', 'c'),
        '5': ('unsigned short', 'H'),
        '6': ('signed short', 'h'),
        '7': ('complete string', 's')
    }
    
    while True:
        print("\nChoose data type to send:")
        for key, value in data_types.items():
            print(f"{key}. {value[0]}")
        
        choice = input("Enter your choice (1-7) or 'q' to quit: ")
        if choice.lower() == 'q':
            break
        
        if choice not in data_types:
            print("Invalid choice. Please try again.")
            continue
        
        data_type, format_char = data_types[choice]
        
        value = input(f"Enter {data_type} value: ")
        
        try:
            if data_type == 'complete string':
                encoded_value = value.encode()
                length = len(encoded_value)
                packed_data = struct.pack(f'cI{length}s', b's', length, encoded_value)
            elif data_type == 'char':
                packed_data = struct.pack(f'cc', b'c', value.encode())
            elif data_type == 'float':
                packed_data = struct.pack(f'cf', b'f', float(value))
            else:
                packed_data = struct.pack(f'c{format_char}', format_char.encode(), int(value))
            
            sock.sendto(packed_data, (host, port))
            print(f"Sent {data_type}: {value} to {host}:{port}")
        except struct.error as e:
            print(f"Error packing data: {e}")
        except ValueError:
            print("Invalid input for the chosen data type.")
        except OSError as e:
            print(f"Error sending data: {e}")
            break

def receive_data(sock, stop_event):
    print("Listening for incoming data...")
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            print(f"\nReceived raw data from {addr}: {data}")
            
            data_type = data[0:1].decode()
            if data_type == 's':
                length = struct.unpack('I', data[1:5])[0]
                value = data[5:5+length].decode()
                print(f"Received complete string: {value}")
            elif data_type == 'c':
                value = data[1:2].decode()
                print(f"Received char: {value}")
            elif data_type == 'f':
                value = struct.unpack('f', data[1:5])[0]
                print(f"Received float: {value}")
            else:
                value = struct.unpack(data_type, data[1:])[0]
                print(f"Received {data_type}: {value}")
        except socket.timeout:
            continue
        except OSError:
            break
    print("Receiving thread stopped.")

def main():
    sock = None
    stop_event = threading.Event()
    receive_thread = None

    while True:
        print("\nUDP Communication Program")
        print("1. Send data")
        print("2. Receive data")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1': 
            if not sock:
                host, port = get_host_port()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.1)
            print(f"Sender mode. Sending to {host}:{port}")
            send_data(sock, host, port)
        elif choice == '2': 
            if not sock:
                host, port = get_host_port()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.1)
                sock.bind((host, port))
            print(f"Receiver mode. Listening on {host}:{port}")
            if not receive_thread or not receive_thread.is_alive():
                receive_thread = threading.Thread(target=receive_data, args=(sock, stop_event))
                receive_thread.start()
            input("Press Enter to return to main menu...\n")
        elif choice == '3': 
            break
        else:
            print("Invalid choice. Please try again.")

    if sock:
        stop_event.set()
        sock.close()
    if receive_thread:
        receive_thread.join()
    print("Program terminated.")

if __name__ == "__main__":
    main()