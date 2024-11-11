from PIL import Image
import cv2
import torch
import function.utils_rotate as utils_rotate
from IPython.display import display
import time
import function.helper as helper


def video_detect(path, yolo_license_plate, yolo_LP_detect, progress_bar):
    prev_frame_time = 0
    new_frame_time = 0
    vid_frame = 0

    # Mở video và lấy tổng số khung hình
    vid = cv2.VideoCapture(path)
    total_frame = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Cấu hình VideoWriter để xuất video
    output = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (frame_width, frame_height))

    while True:
        ret, frame = vid.read()
        if not ret:
            break

        vid_frame += 1
        plates = yolo_LP_detect(frame, size=320)
        list_plates = plates.pandas().xyxy[0].values.tolist()
        list_read_plates = set()

        for plate in list_plates:
            flag = 0
            x = int(plate[0])  # xmin
            y = int(plate[1])  # ymin
            w = int(plate[2] - plate[0])  # xmax - xmin
            h = int(plate[3] - plate[1])  # ymax - ymin  
            crop_img = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (int(plate[0]), int(plate[1])), (int(plate[2]), int(plate[3])), color=(0, 0, 225), thickness=2)

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

        # Tính FPS và hiển thị trên khung hình
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        cv2.putText(frame, str(fps), (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

        # Lưu khung hình vào video đầu ra
        output.write(frame)

        # Cập nhật progress bar
        progress = (vid_frame / total_frame) * 100
        progress_bar['value'] = progress
        progress_bar.update_idletasks()

        # Hiển thị khung hình
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng tài nguyên
    vid.release()
    output.release()
    cv2.destroyAllWindows()
    progress_bar['value'] = 100