from tkinter import *
from database import Base, engine
import tkinter as tk
from tkinter import messagebox
from Controllers.User_Controller import create_user, get_user_by_username
from database import get_db
from tkinter import ttk
import bcrypt
import cv2
import torch
import time
import function.utils_rotate as utils_rotate
import function.helper as helper
from PIL import Image, ImageTk
import urllib
from ultralytics import YOLO
import onnx
import tensorrt as trt

Base.metadata.create_all(bind=engine)

url = "http://192.168.4.67:81"

def admin_view(root):
    value = 0
    # Khởi tạo thiết bị CUDA nếu có
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Tải các mô hình YOLO
    yolo_LP_detect = torch.hub.load('yolov9', 'custom', path='model/Lp_detect.pt', force_reload=True, source='local')
    yolo_LP_detect.to(device)
    yolo_license_plate = torch.hub.load('yolov9', 'custom', path='model/Letter_detect.pt', force_reload=True, source='local')
    yolo_license_plate.to(device)

    # yolo_LP_detect.eval()
    # yolo_license_plate.eval()

    # dummy_input = torch.randn(1, 3, 640, 640)  # Tạo input giả để xuất mô hình
    # onnx_path1 = "model/Lp_detect.onnx"
    # onnx_path2 = "model/Letter_detect.onnx"

    # # Xuất mô hình
    # torch.onnx.export(yolo_LP_detect, dummy_input, onnx_path1, opset_version=11)
    # torch.onnx.export(yolo_license_plate, dummy_input, onnx_path2, opset_version=11)



    container_frame = ttk.Frame(root)
    container_frame.pack(fill="both", expand=True, padx=10, pady=10)

    info_frame = ttk.LabelFrame(container_frame)
    info_frame.grid(column=0, row=0)  # Đặt bên trái container

    # navigate_frame chiếm phần còn lại
    navigate_frame = ttk.LabelFrame(container_frame, text="Navigation", padding=10)
    navigate_frame.grid(column=1, row=0)
    tk.Button(navigate_frame, text="Ai detect", command=lambda: start_detection(info_frame, yolo_license_plate, yolo_LP_detect)).pack(padx=10, pady=10)
    tk.Button(navigate_frame, text="Change Resolution", command=lambda: change_resolution(value)).pack(padx=10, pady=10)
def change_resolution(value):
    value = value+1
    if (value > 13):
        value = 0
    r_url = url + f"/control?var=framesize&val={value}"
    print(r_url)
    webUrl  = urllib.request.urlopen(r_url)
    

def start_detection(parent, yolo_license_plate, yolo_LP_detect):
    # Khởi tạo video capture
    for widget in parent.winfo_children():
        widget.destroy()
    try:
        vid = cv2.VideoCapture(0)
    except:
        return
        
    # Thiết lập các tham số tính FPS
    prev_frame_time = 0
    count = 0
    # Khởi tạo Label để hiển thị video trong info_frame
    # Tạo Listview (Treeview) với 2 cột: ID và Biển số xe
    treeview = ttk.Treeview(parent, columns=("ID", "License Plate"), show="headings")
    treeview.pack(fill="y", side="left")

    # Đặt tiêu đề cột
    treeview.heading("ID", text="ID")
    treeview.heading("License Plate", text="License Plate")
    
    # Chỉnh sửa độ rộng của các cột
    treeview.column("ID", width=100, anchor="center")
    treeview.column("License Plate", width=200, anchor="center")

    video_label = tk.Label(parent)
    video_label.pack(side="left", fill="both", expand=True)  # Make video label fill the frame

    detected_plates = set()

    # Hàm cập nhật khung hình video và nhận diện biển số xe
    def update_frame():
        nonlocal count, prev_frame_time
        count += 1

        # Chỉ lấy mỗi khung hình thứ 3 để giảm tải cho model
        
        ret, frame = vid.read()
        if ret:
            # Phát hiện biển số xe
            plates = yolo_LP_detect(frame, size=320)
            list_plates = plates.pandas().xyxy[0].values.tolist()
            list_read_plates = set()
            # Quá trình nhận diện biển số
            for plate in list_plates:
                flag = 0
                x = int(plate[0])  # xmin
                y = int(plate[1])  # ymin
                w = int(plate[2] - plate[0])  # xmax - xmin
                h = int(plate[3] - plate[1])  # ymax - ymin
                crop_img = frame[y:y + h, x:x + w]
                cv2.rectangle(frame, (int(plate[0]), int(plate[1])), (int(plate[2]), int(plate[3])), color=(0, 0, 225), thickness=2)
                cv2.imwrite("crop.jpg", crop_img)
                rc_image = cv2.imread("crop.jpg")
                lp = ""
                for cc in range(0, 2):
                    for ct in range(0, 2):
                        lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                        if lp != "unknown":
                            list_read_plates.add(lp)
                            cv2.putText(frame, lp, (int(plate[0]), int(plate[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                            flag = 1
                            break
                    if flag == 1:
                        break
            for lp in list_read_plates:
                # Nếu biển số chưa có trong set, thêm vào set và Treeview
                if lp not in detected_plates and helper.is_license_plate(lp):
                    detected_plates.add(lp)  # Thêm vào set đã phát hiện
                    treeview.insert("", "end", values=(len(detected_plates), lp))  # Thêm vào Treeview
            # Tính FPS
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            fps = int(fps)
            # Hiển thị FPS lên video
            # cv2.putText(frame, f"FPS: {fps}", (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3)
            # Chuyển đổi ảnh OpenCV thành ảnh Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)
            # Cập nhật hình ảnh lên label
            video_label.config(image=img_tk)
            video_label.image = img_tk

        # Sau mỗi 20ms sẽ tiếp tục cập nhật khung hình
        video_label.after(1, update_frame)

    # Bắt đầu cập nhật video
    update_frame()

if __name__ == "__main__":
    # root = tk.Tk()
    # root.title("Lincense Plate")
    # admin_view(root)  # Mở form tạo người dùng
    # root.mainloop()
    onnx_model_path = "model/Lp_detect.onnx"
    onnx_model = onnx.load(onnx_model_path)

    # Cấu hình TensorRT builder
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(flags=1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)

    # Parse the ONNX model to TensorRT network
    with open(onnx_model_path, 'rb') as f:
        parser.parse(f.read())

    # Xây dựng mô hình TensorRT
    engine = builder.build_cuda_engine(network)

