import torch
import cv2
import os

# Load YOLO model
yolo_LP_detect = torch.hub.load('yolov9', 'custom', path='model/Letter_detect.pt', force_reload=True, source='local')
yolo_LP_detect.conf = 0.6
# Đọc ảnh
img_path = r"test_img\tải xuống (3).jpg"  # Sử dụng chuỗi thô để tránh lỗi escape
img = cv2.imread(img_path)
img = cv2.resize(img, (640, 640))

if img is None:
    print("Không tìm thấy ảnh. Vui lòng kiểm tra đường dẫn.")
else:
    # Chuyển BGR -> RGB vì YOLO thường xử lý ảnh RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Chạy nhận diện bằng model
    results = yolo_LP_detect(img_rgb, size = 640)
    # Lấy kết quả phát hiện
    detections = results.xyxy[0]  # (x_min, y_min, x_max, y_max, confidence, class)
    # Lặp qua các bounding boxes và crop ảnh
    for i, (*box, conf, cls) in enumerate(detections.tolist()):
        x_min, y_min, x_max, y_max = map(int, box)
        label = f"{results.names[int(cls)]}_{i}"  # Tên class và số thứ tự


        # Vẽ bounding box trên ảnh gốc (tùy chọn)
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(img, f"{results.names[int(cls)]}: {conf:.2f}", 
                    (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imwrite("output.jpg", img)
    cv2.imshow("Detections", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
