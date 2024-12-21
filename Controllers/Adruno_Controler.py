import serial
import time
from threading import Thread

# # Kết nối tới Arduino qua cổng serial
# # arduino = serial.Serial(port='COM7', baudrate=9600, timeout=1)  # Thay 'COM3' bằng cổng của bạn

# def send_command():
#     """Gửi lệnh đến Arduino."""
#     arduino.write("1".encode())  # Gửi lệnh qua serial
#     time.sleep(3)  # Đợi Arduino xử lý
#     arduino.write("0".encode())
#     time.sleep(0.1)

# def onLedandOffLed():
#     thread = Thread(target= send_command)
#     thread.start()

