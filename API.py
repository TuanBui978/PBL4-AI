from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import cv2
import torch
import time
import function.helper as helper
import function.utils_rotate as utils_rotate

app = FastAPI()

# Xác định thiết bị
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

# Tải mô hình
yolo_LP_detect = torch.hub.load('yolov9', 'custom', path='model/Lp_detect.pt', force_reload=True, source='local').to(device)
yolo_license_plate = torch.hub.load('yolov9', 'custom', path='model/Letter_detect.pt', force_reload=True, source='local').to(device)
yolo_license_plate.conf = 0.60

# Hàm tạo luồng video
def generate_video():
    vid = cv2.VideoCapture(0)  # Sử dụng camera
    prev_frame_time = 0
    count = 0
    
    while True:
        count += 1
        ret, frame = vid.read()
        if not ret:
            break
        
        # Nhận diện biển số
        plates = yolo_LP_detect(frame, size=320)
        list_plates = plates.pandas().xyxy[0].values.tolist()
        list_read_plates = set()

        for plate in list_plates:
            x, y, w, h = int(plate[0]), int(plate[1]), int(plate[2]), int(plate[3])
            crop_img = frame[y:h, x:w]

            cv2.rectangle(frame, (x, y), (w, h), color=(0, 0, 225), thickness=2)

            lp = ""
            for cc in range(2):
                for ct in range(2):
                    lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                    if lp != "unknown":
                        list_read_plates.add(lp)
                        cv2.putText(frame, lp, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                        break

        # Tính FPS
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        cv2.putText(frame, str(int(fps)), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

        # Mã hóa khung hình
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_video(), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)