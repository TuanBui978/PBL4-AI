import tkinter as tk
from tkinter import messagebox
from Controllers.License_Plate_Controler import *
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
from datetime import datetime 
import threading
from typing import Callable, Literal
from tkinter import filedialog
import Lp_image as ImageDetect
from Controllers.Adruno_Controler import *
import os
from tkcalendar import Calendar
from Controllers.User_Cotroller import *
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)



url = "http://172.20.10.3"

vid: cv2.VideoCapture = None

def load_model():
    threading.Thread
    global yolo_license_plate, yolo_LP_detect
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    yolo_LP_detect = torch.hub.load('yolov9', 'custom', path='model/Lp_detect.pt', force_reload=True, source='local').to(device)
    yolo_license_plate = torch.hub.load('yolov9', 'custom', path='model/Letter_detect.pt', force_reload=True, source='local').to(device)
    yolo_license_plate.conf = 0.6
    yolo_LP_detect.conf = 0.6
def first_screen(
    parent, 
    task, 
    on_task_success: Callable = None, 
    on_task_failure: Callable = None,
    *task_args, **task_kwargs):
    def do_task(task, *args, **kwargs):
        try:
            task(*args, **kwargs)
            event.set()
            result[0] = True
        except Exception as e:
            result[0] = False
            result[1] = e
            event.set()
    for widget in parent.winfo_children():
        widget.destroy()
    
    
    frame = tk.Frame(parent, width=600, height=400)
    frame.pack_propagate(False)
    frame.pack()

    img = ImageTk.PhotoImage(Image.open("first_screen.jpeg").resize((600, 400), Image.LANCZOS))
    lbl = tk.Label(frame, image=img)
    lbl.img = img
    lbl.place(relx=0.5, rely=0.5, anchor='center')
    progress_bar = ttk.Progressbar(frame, mode="indeterminate")
    progress_bar.pack(side="bottom", fill="x", padx=40, pady= 40)
    event = threading.Event()
    result = [None, None] 
    thread = threading.Thread(target=do_task, args=(task, *task_args), kwargs=task_kwargs)
    thread.start()
    progress_bar.start(10)
    def check_loading():
        if event.is_set():
            progress_bar.stop()
            frame.destroy()
            if result[0] and on_task_success:
                on_task_success()
            elif not result[0] and on_task_failure:
                on_task_failure(result[1])
        else:
            parent.after(100, check_loading)
    check_loading()


def loading_frame(
    parent, 
    task, 
    on_task_success: Callable = None, 
    on_task_failure: Callable = None,
    *task_args, **task_kwargs):
    def do_task(task, *args, **kwargs):
        try:
            task(*args, **kwargs)
            event.set()
            result[0] = True
        except Exception as e:
            result[0] = False
            result[1] = e
            event.set()
    for widget in parent.winfo_children():
        widget.destroy()
    frame = tk.Frame(parent, width=600, height=400)
    frame.pack_propagate(False)
    frame.pack()
    progress_bar = ttk.Progressbar(frame, mode="indeterminate")
    progress_bar.pack(side="left", expand= True ,fill="x", padx=40, pady= 40)
    event = threading.Event()
    result = [None, None] 
    thread = threading.Thread(target=do_task, args=(task, *task_args), kwargs=task_kwargs)
    thread.start()
    progress_bar.start(10)
    def check_loading():
        if event.is_set():
            frame.destroy()
            if result[0] and on_task_success:
                on_task_success()
            elif not result[0] and on_task_failure:
                on_task_failure(result[1])
        else:
            parent.after(100, check_loading)
    check_loading()


def admin_view(root):
    value = 0
    global yolo_LP_detect, yolo_license_plate
    container_frame = ttk.Frame(root)
    container_frame.pack(fill="both", expand=True, padx=10, pady=10)
    info_frame = ttk.LabelFrame(container_frame)
    info_frame.pack(fill="both",side="left", expand=True)
    navigate_frame = ttk.LabelFrame(container_frame, padding=10)
    navigate_frame.pack(side="left", fill="y",expand= True)
    image_detect_button = tk.Button(navigate_frame, text="Image detect", command=lambda: image_detect(info_frame))
    image_detect_button.pack(fill="x", padx=10, pady=10)
    stream_button = tk.Button(navigate_frame, text="Camera Stream", command=lambda: start_detection(info_frame, yolo_license_plate, yolo_LP_detect))
    stream_button.pack(fill="x", padx=10, pady=10)
    stream_button = tk.Button(navigate_frame, text="License Plate Detected", command=lambda: license_plate_detected(info_frame))
    stream_button.pack(fill="x", padx=10, pady=10)
    exit_button = tk.Button(navigate_frame, text= "Exit", command=lambda: root.destroy())
    exit_button.pack(fill="x", padx=10, pady=10, side="bottom")
    image_detect(info_frame)


def load_video(stream, status: Literal["init", "load"] = "init"):
    global vid
    if status == "init":
        # Điều chỉnh kích thước khung hình khi khởi tạo
        r_url = url + "/control?var=framesize&val=8"
        urllib.request.urlopen(r_url)
    # Mở luồng video
    if vid:
        vid.release()
    print(stream)
    vid = cv2.VideoCapture(stream)
    if not vid.isOpened():
        raise Exception("Không thể mở luồng video.")

def change_resolution(value: int):
    global vid
    vid.release()
    r_url = url + f"/control?var=framesize&val={value}"
    urllib.request.urlopen(r_url)
    vid = cv2.VideoCapture(stream)
    if not vid.isOpened():
        raise Exception("Không thể mở luồng video.")

def start_detection(parent, yolo_license_plate, yolo_LP_detect):
    global vid, stream
    for widget in parent.winfo_children():
        widget.destroy()
    if vid:
        vid.release()
    stream = url+":81/stream"
    treeview = ttk.Treeview(parent, columns=("ID", "License Plate", "Timestamp"), show="headings")
    treeview.pack(fill="y", side="left")
    treeview.heading("ID", text="ID")
    treeview.heading("License Plate", text="License Plate")
    treeview.heading("Timestamp", text="Timestamp")
    treeview.column("ID", width=100, anchor="center")
    treeview.column("License Plate", width=100, anchor="center")
    treeview.column("Timestamp", width=200, anchor="center")
    options = [("240x240", 4), ("320x240", 5), ("480x320", 7), ("640x480", 8), ("800x600", 9)] 
    display_options = [f"{label}" for label, value in options]

    combo_box_frame = tk.Frame(parent)
    combo_box_frame.pack(side="top",fill="x", expand=True)


    def on_stream_selection(event):
        global vid
        selected_label = stream_combo_box.get()  # Lấy giá trị stream được chọn từ ComboBox

        for label, value in stream_sources:
            if selected_label == label:  # So sánh chọn với label từ stream_sources
                if selected_label == "Computer camera":
                    resolution_combo_box.config(state="disabled")
                    loading_frame(vid_frame, lambda: load_video(value, "load"), lambda: show_video(vid_frame, treeview))
                else:
                
                    resolution_combo_box.config(state="normal")
                    loading_frame(vid_frame, lambda: load_video(value, "init"), lambda: show_video(vid_frame, treeview))
                break
    stream_sources = [("Computer camera",0), ("ESP-32 CAM", stream)]
    stream_combo_box = ttk.Combobox(combo_box_frame, values=[label for label, value in stream_sources])
    stream_combo_box.grid(column=0, row=0)
    stream_combo_box.bind("<<ComboboxSelected>>", on_stream_selection)
    stream_combo_box.set("Computer camera")

    def on_selection(event):
        global vid
        selected_label = resolution_combo_box.get()
        for label, value in options:
            if label == selected_label:
                loading_frame(vid_frame, lambda: change_resolution(value), lambda: show_video(vid_frame, treeview))
                break
    resolution_combo_box = ttk.Combobox(combo_box_frame, values= display_options)
    resolution_combo_box.grid(column=1, row=0)
    resolution_combo_box.bind("<<ComboboxSelected>>", on_selection)
    resolution_combo_box.set("640x480")
    vid_frame = tk.Frame(parent, height= 480, width=640)
    vid_frame.pack(side="left", fill="both", expand=True)
    resolution_combo_box.config(state="disabled")
    loading_frame(vid_frame, lambda: load_video(0, "load"), lambda: show_video(vid_frame, treeview))
    



def show_video(parent, treeview):
    global vid
    for widget in parent.winfo_children():
        widget.destroy()
    prev_frame_time = 0
    count = 0
    video_label = tk.Label(parent)
    video_label.pack(side="left", fill="both", expand=True)  # Make video label fill the frame
    detected_plates = set()
    plate_stability = {}  # Lưu trạng thái ổn định của biển số

    def update_frame():
        nonlocal count, prev_frame_time
        ret, frame = vid.read()
        if ret:
            # Phát hiện biển số xe
            plates = yolo_LP_detect(frame, size=640)
            list_plates = plates.pandas().xyxy[0].values.tolist()
            list_read_plates = set()
            
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

            # Kiểm tra sự ổn định của biển số
            for lp in list_read_plates:
                if helper.is_license_plate(lp):  # Kiểm tra nếu đúng định dạng biển số
                    if lp not in detected_plates:
                        # Tăng đếm số lần nhận diện liên tiếp
                        plate_stability[lp] = plate_stability.get(lp, 0) + 1
                        
                        # Nếu đã nhận diện ổn định (ví dụ: 5 lần liên tiếp)
                        if plate_stability[lp] >= 10:
                            path = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  
                            detected_plates.add(lp)  # Thêm vào set đã phát hiện
                            treeview.insert("", "end", values=(len(detected_plates), lp, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            del plate_stability[lp]  # Xóa khỏi kiểm tra ổn định sau khi thêm vào
                            frame_path = os.path.join("Result", f"{path}.jpg")
                            add_license_plate(lp, datetime.now(), frame_path)
                            changeServo()
                            cv2.imwrite(frame_path, frame)
                            # onLedandOffLed()
                    else:
                        plate_stability.pop(lp, None)  # Xóa nếu biển số đã được thêm

            # Tính FPS
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            fps = int(fps)

            # Hiển thị video
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)
            video_label.config(image=img_tk)
            video_label.image = img_tk

        video_label.after(1, update_frame)

    update_frame()


def choose_file(label, image_label):
    file_path = filedialog.askopenfilename(
        title="Chọn tệp",
        filetypes=[("Image files", "*.jpg;*.png")]
    )
    if file_path:
        print(f"Đã chọn tệp: {file_path}")
        label.set(f"{file_path}")
        image = ImageDetect.start_detection(file_path, yolo_license_plate, yolo_LP_detect)
        frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((640, 640), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk


def image_detect(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    frame = tk.Frame(parent)
    frame.pack(fill="x", expand=True)
    text = tk.StringVar()
    text.set("Chưa chọn tệp")
    label = tk.Entry(frame, textvariable=text, state="readonly", width=40)
    label.pack(side="left", fill="x", padx=5, expand=True)

    button = tk.Button(frame, text="Chọn tệp", command=lambda: choose_file(text, image_label))
    button.pack(side="left",padx=5)

    image = Image.new("RGB", (640, 640), color="white")
    image_tk = ImageTk.PhotoImage(image)
    image_label = tk.Label(parent, image=image_tk)
    image_label.pack()
    image_label.image = image_tk

def open_calendar(parent, combo: ttk.Combobox):
    """Hiển thị dialog chọn ngày"""
    def select_date():
        """Lấy ngày đã chọn và đặt vào Combobox"""
        selected_date = cal.get_date()
        
        combo.set(selected_date)
        top.destroy()

    # Tạo cửa sổ con (Toplevel)
    top = tk.Toplevel(parent)
    top.title("Chọn ngày")
    top.geometry("300x300")

    # Thêm lịch
    cal = Calendar(top, selectmode='day', year=2024, month=11, day=21, date_pattern="dd/mm/yyyy")
    cal.pack(pady=20)

    # Nút xác nhận
    btn = ttk.Button(top, text="Xác nhận", command=select_date)
    btn.pack(pady=10)

def license_plate_detected(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    
    frame = tk.Frame(parent, width=600, height=480)
    frame.pack(side="right")
    image_label = tk.Label(frame)
    image_label.pack(fill="both", expand=True)

    info_frame = tk.Frame(parent)
    info_frame.pack(side="top", fill='x')


    entry_license_plate = tk.Entry(info_frame,)
    entry_license_plate.pack(expand=True, fill="x", side="top")



    time_frame = tk.Frame(info_frame)
    time_frame.pack(expand=True, fill="x", side="top")

    text = tk.Label(time_frame, text="From", width=5, justify="left", anchor="w")
    text.pack_propagate(False)
    text.pack(side="left")
    fromDay = ttk.Combobox(time_frame)
    fromDay.bind("<Button-1>", lambda event: open_calendar(parent, fromDay))
    fromDay.pack(side="left", fill="x", expand=True, padx=(5,0))

    text2 = tk.Label(time_frame, text="To", width=5, justify="left", anchor="w")
    text2.pack_propagate(False)
    text2.pack(side="left")
    to = ttk.Combobox(time_frame)
    to.bind("<Button-1>", lambda event: open_calendar(parent, to))
    to.pack(side="left", fill="x", expand=True, padx=(5,0))

    # Nút Lọc
    filter_button = tk.Button(time_frame, text="Filter", command=lambda: filter_data(fromDay, to))
    filter_button.pack(side="left", padx=5)

    treeview = ttk.Treeview(parent, columns=("ID", "License Plate", "Timestamp"), show="headings")
    treeview.pack(expand=True, fill="both", side="top")
    treeview.heading("ID", text="ID")
    treeview.heading("License Plate", text="License Plate")
    treeview.heading("Timestamp", text="Timestamp")
    treeview.column("ID", width=100, anchor="center")
    treeview.column("License Plate", width=100, anchor="center")
    treeview.column("Timestamp", width=200, anchor="center")

    plates = get_all_license_plate()
    for plate in plates:
        treeview.insert("", "end", values=(plate.id, plate.license_plate, plate.time.strftime("%d/%m/%Y %H:%M:%S")))

    def onTextChangeListener(text):
        for item in treeview.get_children():
            treeview.delete(item)
        plates = get_license_plate_by_plate_num(text)
        for plate in plates:
            treeview.insert("", "end", values=(plate.id, plate.license_plate, plate.time.strftime("%d/%m/%Y %H:%M:%S")))

    setOnTextChangeListener(entry=entry_license_plate, onTextChangeListener=onTextChangeListener)

    def filter_data(fromDay, to):
        """Lọc dữ liệu từ ngày đã chọn đến ngày đã chọn"""
        from_date = fromDay.get()
        to_date = to.get()

        # Chuyển đổi định dạng ngày
        try:
            from_date = datetime.strptime(from_date, "%d/%m/%Y")
            to_date = datetime.strptime(to_date, "%d/%m/%Y")
        except ValueError:
            print("Định dạng ngày không hợp lệ")
            return

        # Truy vấn dữ liệu
        filtered_plates = get_license_plate_by_date_range(from_date, to_date)
        for item in treeview.get_children():
            treeview.delete(item)
        for plate in filtered_plates:
            treeview.insert("", "end", values=(plate.id, plate.license_plate, plate.time.strftime("%d/%m/%Y %H:%M:%S")))

    def on_item_click(event):
        selected_item = treeview.selection()
        if selected_item:
            item_values = treeview.item(selected_item)["values"]
            plate_id = item_values[0]
            plate = get_license_plate_by_id(plate_id)
            file_path = plate.image_path
            if file_path:
                image = cv2.imread(file_path)
                if image is not None:
                    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((640, 640), Image.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    image_label.config(image=img_tk)
                    image_label.image = img_tk

    treeview.bind("<ButtonRelease-1>", on_item_click)
def setOnTextChangeListener(entry, onTextChangeListener: Callable):
    text_var = tk.StringVar()
    text_var.trace_add("write", lambda *args: onTextChangeListener(text_var.get()))
    entry.config(textvariable=text_var)





def video_detect(parent):
    for widget in parent.winfo_children():
        widget.destroy()
    frame = tk.Frame(parent)
    frame.pack(fill="x", expand=True)
    text = tk.StringVar()
    text.set("Chưa chọn tệp")
    label = tk.Entry(frame, textvariable=text, state="readonly", width=40)
    label.pack(side="left", fill="x", padx=5, expand=True)
    button = tk.Button(frame, text="Chọn tệp", command=lambda: choose_file(text, image_label))
    button.pack(side="left",padx=5)
    image = Image.new("RGB", (640, 640), color="white")
    image_tk = ImageTk.PhotoImage(image)
    image_label = tk.Label(parent, image=image_tk)
    image_label.pack()
    image_label.image = image_tk
    return
# def show_create_user_form(root):
#     def submit():
#         username = entry_username.get()
#         password = entry_password.get()
#         retype_password = entry_retype_password.get()
#         name = entry_name.get()
#         address = entry_address.get()
#         cccd = entry_cccd.get()

#         if retype_password != password:
#             messagebox.showerror("Error", "Passwords do not match!")
#             return

#         if not all([username, password, retype_password, name, address, cccd]):
#             messagebox.showerror("Error", "Please fill all fields")
#             return

#         with next(get_db()) as db:
#             if create_user(name=name, username=username, password=password, cccd=cccd, address=address, db=db) is None:
#                 messagebox.showerror("Error", "User already exists!")
#                 return

#             messagebox.showinfo("Success", "User created successfully!")
#             frame.destroy()
#             switch_login()

#     def switch_login():
#         frame.destroy()
#         login_form(root)

#     # Tạo Frame để chứa các widget
#     frame = ttk.Frame(root, padding=10)
#     frame.pack(expand=True)

#     # Username Label và Entry
#     tk.Label(frame, text="Username", anchor='w').pack(fill='x', pady=5)
#     entry_username = ttk.Entry(frame, width=40)
#     entry_username.pack(pady=5)

#     # Password Label và Entry
#     tk.Label(frame, text="Password", anchor='w').pack(fill='x', pady=5)
#     entry_password = ttk.Entry(frame, width=40, show="*")
#     entry_password.pack(pady=5)

#     # Retype Password Label và Entry
#     tk.Label(frame, text="Retype Password", anchor='w').pack(fill='x', pady=5)
#     entry_retype_password = ttk.Entry(frame, width=40, show="*")
#     entry_retype_password.pack(pady=5)

#     # Name Label và Entry
#     tk.Label(frame, text="Name", anchor='w').pack(fill='x', pady=5)
#     entry_name = ttk.Entry(frame, width=40)
#     entry_name.pack(pady=5)

#     # Address Label và Entry
#     tk.Label(frame, text="Address", anchor='w').pack(fill='x', pady=5)
#     entry_address = ttk.Entry(frame, width=40)
#     entry_address.pack(pady=5)

#     # CCCD Label và Entry
#     tk.Label(frame, text="CCCD", anchor='w').pack(fill='x', pady=5)
#     entry_cccd = ttk.Entry(frame, width=40)
#     entry_cccd.pack(pady=5)

#     # Nút tạo người dùng
#     button_frame = ttk.Frame(frame)
#     button_frame.pack(pady=10)

#     # Nút tạo người dùng và nút đăng ký
#     tk.Button(button_frame, text="Register", command=submit).pack(side="left", padx=5)
#     tk.Button(button_frame, text="Login", command=lambda: switch_login()).pack(side="left", padx=5)

#     root.mainloop()

# def login_form(root):
#     def submit():
#         username = entry_username.get()
#         password = entry_password.get()

#         if not all([username, password]):
#             messagebox.showerror("Error", "Please enter both username and password")
#             return

#         with next(get_db()) as db:
#             user = login_user(username=username, password=password, db=db)

#             if not user:
#                 messagebox.showerror("Error", "Invalid username or password")
#                 return

#             frame.destroy()
#             admin_view(root)

#     def switch_register():
#         frame.destroy()
#         show_create_user_form(root)

#     # Tạo Frame để chứa các widget
#     frame = ttk.Frame(root, padding=10)
#     frame.pack(expand=True)

#     # Username Label và Entry
#     tk.Label(frame, text="Username", anchor='w').pack(fill='x', pady=5)
#     entry_username = ttk.Entry(frame, width=40)
#     entry_username.pack(pady=5)

#     # Password Label và Entry
#     tk.Label(frame, text="Password", anchor='w').pack(fill='x', pady=5)
#     entry_password = ttk.Entry(frame, width=40, show="*")
#     entry_password.pack(pady=5)

#     # Nút tạo người dùng
#     button_frame = ttk.Frame(frame)
#     button_frame.pack(pady=10)

#     # Nút tạo người dùng và nút đăng ký
#     tk.Button(button_frame, text="Login", command=submit, bg="blue", fg="white", width=10, height=2).pack(side="left", padx=5)
#     tk.Button(button_frame, text="Register", command=lambda: switch_register(), bg="green", fg="white", width=10, height=2).pack(side="left", padx=5)



#     root.mainloop()
