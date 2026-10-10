# Hand Detection - Ảo thuật cùng thị giác máy tính

Ứng dụng Computer Vision kết hợp giữa **OpenCV** và **MediaPipe** để phát hiện bàn tay và xây dựng các ứng dụng tương tác không chạm thú vị.

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

## Cấu Trúc Thư Mục

```text
Project_Hand-Detection/
├── Fingers/                # Chứa ảnh minh họa số lượng ngón tay (0 - 5 ngón)
│   ├── 0.png
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   ├── 4.png
│   └── 5.png
├── count_fingers.py        # Ứng dụng đếm số lượng ngón tay theo thời gian thực
├── hand.py                 # Module cốt lõi nhận diện & theo dõi bàn tay (handDetector)
├── keyboard.py             # Ứng dụng bàn phím ảo không chạm (Virtual Keyboard)
├── volume.py               # Ứng dụng điều khiển âm lượng hệ thống bằng cử chỉ
├── requirements.txt        # Danh sách các thư viện phụ thuộc
└── README.md               # Tài liệu hướng dẫn sử dụng dự án
```

## Chức Năng 4 File Python

### 1. `hand.py` — Module Phát Hiện & Theo Dõi Bàn Tay (Core Module)
- **Mục đích:** Đóng vai trò là module nền tảng chứa lớp `handDetector`, cung cấp các phương thức nhận diện và trích xuất tọa độ bàn tay cho toàn bộ dự án.
- **Tính năng chính:**
  - Khởi tạo và đóng gói bộ giải pháp `mp.solutions.hands`.
  - Tìm kiếm và vẽ 21 điểm mốc (landmarks) cùng các đường nối xương bàn tay (`findHands`).
  - Trích xuất tọa độ pixel `(x, y)` của từng điểm mốc theo kích thước khung hình (`findPosition`).
- **Chi tiết kỹ thuật:**
  - **Pipeline màu:** Chuyển đổi không gian màu BGR sang RGB (`cv2.cvtColor`) phù hợp với đầu vào của mô hình MediaPipe.
  - **Quy đổi tọa độ:** MediaPipe trả về tọa độ chuẩn hóa $[0, 1]$, module nhân với kích thước ảnh $(w, h)$ để thu được tọa độ pixel thực tế $cx = \text{int}(lm.x \times w)$, $cy = \text{int}(lm.y \times h)$.
  - **Tối ưu Detection & Tracking:** Cấu hình `static_image_mode=False` giúp mô hình chỉ kích hoạt detector khi mất dấu; các khung hình sau chuyển sang tracking theo dõi vị trí mốc cũ, tối ưu FPS khi stream webcam.
- **Cách chạy:**
  ```bash
  python hand.py
  ```

### 2. `count_fingers.py` — Ứng Dụng Đếm Số Ngón Tay (Finger Counter)
- **Mục đích:** Nhận diện và đếm số lượng ngón tay đang giơ lên theo thời gian thực qua webcam.
- **Tính năng chính:**
  - Đếm chính xác từ 0 đến 5 ngón tay trên một bàn tay.
  - Hiển thị số lượng ngón tay kèm ảnh minh họa cử chỉ tương ứng từ thư mục `Fingers/`.
  - Nhận diện cử chỉ đặc biệt (giơ ngón giữa) và hiển thị thông báo.
- **Chi tiết kỹ thuật:**
  - **Phân loại tay Trái/Phải:** So sánh hoành độ giữa khớp gốc ngón trỏ (landmark 5) và khớp gốc ngón út (landmark 17): nếu $x_5 < x_{17}$ là tay phải (với lòng bàn tay hướng về camera), ngược lại là tay trái.
  - **Logic ngón cái (Trục X):** Với tay phải, ngón cái mở khi đỉnh ngón nằm lệch trái so với khớp IP ($x_4 < x_3$); với tay trái thì ngược lại ($x_4 > x_3$).
  - **Logic 4 ngón dài (Trục Y):** Hệ trục Y của ảnh hướng xuống dưới; một ngón mở khi tung độ đỉnh ngón nhỏ hơn tung độ khớp đốt thứ hai ($y_{tip} < y_{pip}$, ví dụ: $y_8 < y_6$).
  - **Overlay hình ảnh:** Ghi đè ma trận điểm ảnh minh họa trực tiếp lên góc khung hình bằng kỹ thuật slicing của NumPy (`frame[0:h, 0:w] = img`).
- **Cách chạy:**
  ```bash
  python count_fingers.py
  ```

### 3. `keyboard.py` — Bàn Phím Ảo Không Chạm (Virtual Keyboard)
- **Mục đích:** Tạo bàn phím ảo hiển thị trên màn hình, cho phép người dùng gõ chữ thông qua cử chỉ ngón tay trước camera.
- **Tính năng chính:**
  - Vẽ bố cục bàn phím QWERTY 3 hàng phím trực tiếp trên khung hình camera (`class Button`).
  - Hỗ trợ phản hồi màu sắc theo 3 trạng thái: Mặc định (trắng), Rê phím (xám sáng), Nhấn phím (xám đậm).
  - Hiển thị văn bản đã gõ với hiệu ứng viền chữ rõ nét.
- **Chi tiết kỹ thuật:**
  - **Kiểm tra va chạm (AABB Collision):** Hàm `finger_pointing` kiểm tra tọa độ đỉnh ngón trỏ $(x_8, y_8)$ có nằm trong hộp bao của phím hay không ($x_{pos} \le x_8 \le x_{pos} + size$ và $y_{pos} \le y_8 \le y_{pos} + size$).
  - **Logic cử chỉ Click:** Kích hoạt nhấn phím khi ngón trỏ giơ cao ($y_8 < y_6$), ngón cái gập ($x_4 < x_2$) và cả 3 ngón còn lại đều gập ($y_{12} > y_{10}, y_{16} > y_{14}, y_{20} > y_{18}$).
  - **Debounce chống dội phím:** Áp dụng `time.sleep(2)` ngay sau khi ghi nhận ký tự để tạm khóa phím, tránh hiện tượng gõ lặp chữ ngoài ý muốn do tốc độ khung hình cao.
  - **Vẽ viền chữ (Text Outline):** Chồng 2 lớp `cv2.putText` tại cùng tọa độ: lớp viền nét dày màu trắng (`thickness=12`) bên dưới và lớp chữ nét mỏng (`thickness=4`) bên trên, giúp chữ hiển thị rõ trên mọi phông nền.
- **Cách chạy:**
  ```bash
  python keyboard.py
  ```

### 4. `volume.py` — Điều Khiển Âm Lượng Hệ Thống (Gesture Volume Control)
- **Mục đích:** Tăng/giảm âm lượng loa của máy tính Windows bằng khoảng cách giữa hai ngón tay.
- **Tính năng chính:**
  - Điều chỉnh Master Volume thực tế của máy tính Windows theo cử chỉ hai ngón tay.
  - Trực quan hóa thanh âm lượng (Volume Bar) và tỷ lệ phần trăm (0% - 100%).
  - Đổi màu cảnh báo trực quan khi chạm hai đầu ngón tay (mức âm lượng tối thiểu).
- **Chi tiết kỹ thuật:**
  - **Khoảng cách Euclid:** Dùng `math.hypot(x_1 - x_2, y_1 - y_2)` để đo khoảng cách pixel thực tế giữa đỉnh ngón cái (landmark 4) và đỉnh ngón trỏ (landmark 8).
  - **Nội suy tuyến tính (`np.interp`):** Ánh xạ khoảng cách đo được $[25, 180]$ pixel sang 3 dải giá trị: dải dB âm lượng Windows $[minVol, maxVol]$ (thường từ $-65.25$ dB đến $0.0$ dB), chiều cao thanh Volume Bar $[400, 150]$ (đảo ngược do trục Y hướng xuống), và phần trăm $[0, 100]\%$.
  - **Giao tiếp Windows Core Audio:** Kết nối Endpoint loa thông qua COM interface `IAudioEndpointVolume` của thư viện `pycaw`, gán mức âm lượng bằng `volume.SetMasterVolumeLevel(vol, None)`.
- **Cách chạy:**
  ```bash
  python volume.py
  ```

## Lưu Ý Khi Sử Dụng
- Nhấn phím **`q`** trên bàn phím khi đang ở cửa sổ hiển thị camera để thoát chương trình.
- Cả 4 ứng dụng đều cấu hình backend `cv2.CAP_DSHOW` giúp khởi động camera nhanh và hoạt động ổn định trên hệ điều hành Windows.