import os
import shutil

def delete_pycache_folders(directory):
    """
    Tìm và xóa tất cả các thư mục '__pycache__' trong cây thư mục.
    """
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in dirs:
            folder_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(folder_path)
                print(f"[✔️] Đã xóa: {folder_path}")
            except Exception as e:
                print(f"[❌] Lỗi khi xóa {folder_path}: {e}")

if __name__ == "__main__":
    project_path = os.getcwd()  # Lấy thư mục hiện tại
    print(f"🔍 Đang tìm và xóa '__pycache__' trong: {project_path}")
    delete_pycache_folders(project_path)
    print("✅ Hoàn tất!")
