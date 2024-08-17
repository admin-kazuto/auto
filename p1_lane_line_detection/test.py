import cv2
import os

def extract_frames(video_path, output_folder, txt_file_path):
    # Mở video
    cap = cv2.VideoCapture(video_path)
    
    # Kiểm tra xem video có mở được không
    if not cap.isOpened():
        print("Không thể mở video.")
        return
    
    # Đảm bảo thư mục đầu ra tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Mở file TXT để ghi tên ảnh
    with open(txt_file_path, 'w') as txt_file:
        frame_count = 0
        while True:
            # Đọc một khung hình
            ret, frame = cap.read()
            
            # Nếu không còn khung hình nào thì thoát
            if not ret:
                break
            
            # Tạo đường dẫn cho khung hình
            frame_name = f"frame_{frame_count:04d}.jpg"
            frame_path = os.path.join(output_folder, frame_name)
            
            # Lưu khung hình vào thư mục đầu ra
            cv2.imwrite(frame_path, frame)
            
            # Ghi tên khung hình vào file TXT
            txt_file.write(frame_name + '\n')
            
            frame_count += 1
    
    # Giải phóng bộ nhớ
    cap.release()
    print(f"Đã lưu {frame_count} khung hình vào thư mục {output_folder} và ghi tên vào file {txt_file_path}.")

# Đường dẫn đến video và file TXT
video_path = "5741328582801.mp4"
output_folder = "frames_output"
txt_file_path = "test.txt"

# Gọi hàm extract_frames
extract_frames(video_path, output_folder, txt_file_path)
