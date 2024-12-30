import serial
import time
from threading import Thread

# Biến toàn cục để lưu kết nối serial
arduino = None

def connect_arduino():
    """Kết nối với Arduino qua cổng serial, nếu gặp lỗi sẽ bỏ qua."""
    global arduino
    try:
        arduino = serial.Serial(port='COM10', baudrate=9600, timeout=1)
        print("Arduino connected successfully.")
    except serial.SerialException as e:
        print(f"Error connecting to Arduino: {e}")

def send_command():
    """Gửi lệnh đến Arduino nếu kết nối thành công."""
    if arduino is not None:
        try:
            arduino.write(b'1')  # Gửi lệnh '1' dưới dạng bytes
            time.sleep(3)        # Đợi 3 giây
            arduino.write(b'0')  # Gửi lệnh '0' để tắt servo
        except Exception as e:
            print(f"Error sending command to Arduino: {e}")
    else:
        print("No Arduino connection. Command not sent.")

def changeServo():
    """Khởi tạo và chạy luồng gửi lệnh."""
    thread = Thread(target=send_command)
    thread.start()  # Dùng start để tạo luồng mới

def stopArduino():
    """Đóng cổng serial nếu kết nối thành công."""
    if arduino is not None:
        arduino.close()
        print("Arduino connection closed.")
    else:
        print("No Arduino connection to close.")

# Ví dụ sử dụng
            # Đóng kết nối serial sau khi hoàn thành
