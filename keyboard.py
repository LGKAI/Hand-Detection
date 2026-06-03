import cv2
import time
import hand as htm

class Button:
    def __init__(self, pos, text):
        self.pos = pos
        self.text = text
        
    def draw(self, frame, color):
        pt = [self.pos[0] + BUTTON_SIZE, self.pos[1] + BUTTON_SIZE]
        # Vẽ phím
        cv2.rectangle(frame, self.pos, pt, color, cv2.FILLED)
        # Viết chữ lên phím
        cv2.putText(frame, self.text, [self.pos[0] + BUTTON_SIZE // 5, pt[1] - BUTTON_SIZE // 5], 
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

def finger_pointing(finger, button): # Hàm kiểm tra ngón trỏ hover vào phím
    # finger: [id, x, y]
    # button.pos: [x, y]
    return (button.pos[0] <= finger[1] <= button.pos[0] + BUTTON_SIZE and 
            button.pos[1] <= finger[2] <= button.pos[1] + BUTTON_SIZE)

if __name__ == "__main__":
    X_START, Y_START = 50, 50
    BUTTON_SIZE = 70
    BUTTON_GAP = 30
    MY_KEYBOARD = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    ]

    final_text = ""

    cap = cv2.VideoCapture(0)
    cap.set(3, cap.get(3) * 2)
    cap.set(4, cap.get(4) * 2)
    pTime = time.time()
    detector = htm.handDetector(detectionCon=0.5)
    
    while True:
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame, draw=False)
        
        # FPS
        cTime = time.time()
        fps = int(1 / (cTime - pTime))
        pTime = cTime
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)
        
        if len(lmList) != 0:
            # Lấy ID của đỉnh ngón trỏ
            finger_index = lmList[8] # [8, x, y]
            
            # 1. Xác định trạng thái của các ngón tay để tạo cử chỉ CLICK
            # Lưu ý Y MediaPipe tăng xuống dưới, nên Y đỉnh < Y khớp là giơ
            # Ngón trỏ (8) phải giơ ra
            is_index_open = lmList[8][2] < lmList[6][2]
            # Ngón cái (4) gập (dựa vào X so với khớp MCP ID 2)
            is_thumb_closed = lmList[4][1] < lmList[2][1]
            # 3 ngón còn lại gập (đỉnh Y > khớp Y)
            is_middle_closed = lmList[12][2] > lmList[10][2]
            is_ring_closed = lmList[16][2] > lmList[14][2]
            is_pinky_closed = lmList[20][2] > lmList[18][2]
            # Định nghĩa cử chỉ CLICK: Trỏ giơ VÀ cả 4 ngón còn lại gập
            click_gesture = (is_index_open and is_thumb_closed and 
                            is_middle_closed and is_ring_closed and is_pinky_closed)
            
            # 2. Kiểm tra tương tác với bàn phím
            for i in range(0, 3):
                for j in range(len(MY_KEYBOARD[i])):
                    # Tạo đối tượng nút
                    pos = [Y_START + j * (BUTTON_SIZE + BUTTON_GAP), X_START + i * (BUTTON_SIZE + BUTTON_GAP)]
                    cur_button = Button(pos, MY_KEYBOARD[i][j])
                    # Kiểm tra HOVER
                    if finger_pointing(finger_index, cur_button):
                        # Kiểm tra CLICK
                        if click_gesture:
                            # Trạng thái CLICK
                            cur_button.draw(frame, (128, 128, 128))
                            final_text += cur_button.text
                            time.sleep(2) # Tạm dừng để tránh gõ đúp chữ
                        else:
                            # Trạng thái HOVER
                            cur_button.draw(frame, (192, 192, 192))
                    else:
                        # Trạng thái mặc định
                        cur_button.draw(frame, (255, 255, 255))
                        
            # Vẽ chấm tròn ở ngón trỏ để dễ nhìn mục tiêu
            cv2.circle(frame, (finger_index[1], finger_index[2]), 10, (0, 0, 255), -1)

        else:
            # Khi không có tay, vẽ bàn phím mặc định
            for i in range(0, 3):
                for j in range(len(MY_KEYBOARD[i])):
                    pos = [Y_START + j * (BUTTON_SIZE + BUTTON_GAP), X_START + i * (BUTTON_SIZE + BUTTON_GAP)]
                    cur_button = Button(pos, MY_KEYBOARD[i][j])
                    cur_button.draw(frame, (255, 255, 255))

        # Hiển thị văn bản đã gõ
        # 1. Vẽ viền màu trắng (nét dày = 12)
        cv2.putText(frame, final_text, (50, 650), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 12)
        # 2. Vẽ chữ màu đen đè lên trên (nét mỏng = 4)
        cv2.putText(frame, final_text, (50, 650), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 4)

        cv2.imshow('Keyboard', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()