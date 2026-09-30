# Hand Detection - Ảo thuật cùng thị giác máy tính

Ứng dụng Computer Vision kết hợp giữa OpenCV và MediaPipe để phát hiện bàn tay và xây dựng các ứng dụng tương tác không chạm thú vị.

## Hướng Dẫn Cài Đặt

1. **Tạo và kích hoạt môi trường ảo (khuyến nghị Python 3.11):**
   ```text
   py -3.11 -m venv venv
   .\venv\Scripts\activate
   ```

2. **Cài đặt các thư viện cần thiết:**
   ```text
   pip install -r requirements.txt
   ```

## Chức Năng 4 File Python

### 1. `hand.py` — Module Phát Hiện & Theo Dõi Bàn Tay (Core Module)
- **Mục đích:** Đóng vai trò là module nền tảng chứa lớp `handDetector`, cung cấp các phương thức nhận diện và trích xuất tọa độ bàn tay cho toàn bộ dự án.
- **Tính năng chính:**
  - Sử dụng MediaPipe Hands để tìm kiếm và vẽ 21 điểm mốc (landmarks) cùng các liên kết xương bàn tay (`findHands`).
  - Trích xuất tọa độ `(x, y)` theo pixel của từng điểm mốc bàn tay (`findPosition`).
  - Có thể chạy độc lập để kiểm tra webcam, hiển thị khung hình kèm chỉ số FPS.
- **Cách chạy:**
  ```bash
  python hand.py
  ```

### 2. `count_fingers.py` — Ứng Dụng Đếm Số Ngón Tay (Finger Counter)
- **Mục đích:** Nhận diện và đếm số lượng ngón tay đang giơ lên theo thời gian thực qua webcam.
- **Tính năng chính:**
  - Tự động phân biệt tay trái và tay phải để xác định chính xác cử chỉ mở/gập của ngón cái.
  - Kiểm tra trạng thái đóng/mở của 4 ngón còn lại (ngón trỏ, giữa, áp út, út) dựa trên tọa độ đỉnh ngón so với các khớp đốt ngón.
  - Hiển thị số lượng ngón tay đang mở kèm ảnh minh họa cử chỉ tương ứng từ thư mục `Fingers/`.
  - Có cử chỉ nhận diện đặc biệt khi giơ ngón giữa.
- **Cách chạy:**
  ```bash
  python count_fingers.py
  ```

### 3. `keyboard.py` — Bàn Phím Ảo Không Chạm (Virtual Keyboard)
- **Mục đích:** Tạo bàn phím ảo hiển thị trên màn hình, cho phép người dùng gõ chữ thông qua cử chỉ ngón tay trước camera.
- **Tính năng chính:**
  - Vẽ giao diện các nút phím theo bố cục QWERTY (`class Button`).
  - **Cử chỉ Hover (Rê phím):** Đưa đỉnh ngón trỏ (landmark 8) vào vùng phím, phím sẽ đổi màu xám sáng để nhận diện đang trỏ tới.
  - **Cử chỉ Click (Nhấn phím):** Giơ ngón trỏ và gập cả 4 ngón còn lại (ngón cái, giữa, áp út, út) để thực hiện thao tác gõ phím (phím đổi màu xám đậm).
  - Tích hợp độ trễ ngắn (`time.sleep`) để chống dội phím (tránh gõ lặp chữ ngoài ý muốn).
  - Hiển thị văn bản đã gõ trực tiếp lên màn hình camera.
- **Cách chạy:**
  ```bash
  python keyboard.py
  ```

### 4. `volume.py` — Điều Khiển Âm Lượng Hệ Thống (Gesture Volume Control)
- **Mục đích:** Tăng/giảm âm lượng loa của máy tính Windows bằng khoảng cách giữa hai ngón tay.
- **Tính năng chính:**
  - Kết nối và can thiệp Master Volume của Windows thông qua thư viện `pycaw`.
  - Theo dõi tọa độ giữa đỉnh ngón cái (landmark 4) và đỉnh ngón trỏ (landmark 8), tính toán khoảng cách giữa chúng.
  - Sử dụng hàm nội suy `np.interp` để ánh xạ khoảng cách ngón tay sang mức âm lượng hệ thống thực tế (dB) và tỷ lệ % (0% - 100%).
  - Vẽ trực quan thanh âm lượng (Volume Bar), đường nối giữa hai đầu ngón tay và đổi màu cảnh báo khi chạm 2 đầu ngón tay (mức âm lượng tối thiểu).
- **Cách chạy:**
  ```bash
  python volume.py
  ```

## Lưu Ý Khi Sử Dụng
- Nhấn phím **`q`** trên bàn phím khi đang ở cửa sổ hiển thị camera để thoát chương trình.
- Cả 4 ứng dụng đều cấu hình backend `cv2.CAP_DSHOW` giúp khởi động camera nhanh và hoạt động ổn định trên hệ điều hành Windows.