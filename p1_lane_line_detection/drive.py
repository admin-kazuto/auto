import asyncio
import websockets
from PIL import Image
import json
import cv2
import numpy as np
import base64
from io import BytesIO
import os
from lane_line_detection import calculate_control_signal

# Hàm lưu khung hình và ghi tên vào file
def save_frame(frame, output_folder, txt_file, frame_count):
    # Đảm bảo thư mục đầu ra tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Tạo đường dẫn cho khung hình
    frame_name = f"frame_{frame_count:04d}.jpg"
    frame_path = os.path.join(output_folder, frame_name)
    
    # Lưu khung hình
    cv2.imwrite(frame_path, frame)
    
    # Ghi tên khung hình vào file txt
    txt_file.write(frame_name + '\n')

async def echo(websocket, path):
    # Mở file để ghi tên các khung hình
    with open("test.txt", 'w') as txt_file:
        frame_count = 0
        async for message in websocket:
            # Nhận hình ảnh từ mô phỏng
            data = json.loads(message)
            image = Image.open(BytesIO(base64.b64decode(data["image"])))
            image = np.asarray(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Chuẩn bị hình ảnh để hiển thị
            draw = image.copy()

            # Gửi lại giá trị throttle và góc lái
            throttle, steering_angle = calculate_control_signal(image, draw=draw)

            # Hiển thị kết quả trong một cửa sổ
            cv2.imshow("Result", draw)
            cv2.waitKey(1)

            # Lưu khung hình hiện tại
            save_frame(draw, "frames_output", txt_file, frame_count)
            frame_count += 1

            # Gửi lại giá trị throttle và góc lái
            message = json.dumps({"throttle": throttle, "steering": steering_angle})
            print(message)
            await websocket.send(message)

async def main():
    print("Bắt đầu server...")
    async with websockets.serve(echo, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # chạy mãi mãi

# Bắt đầu server
asyncio.run(main())
