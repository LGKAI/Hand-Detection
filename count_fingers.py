import cv2
import time
import os
import hand as htm

if __name__ == "__main__":
    pTime = 0
    cap = cv2.VideoCapture(0)

    folderPath = "./Fingers"
    lst = os.listdir(folderPath)
    lst2 = []
    for i in lst:
        image = cv2.imread(f"{folderPath}/{i}")
        lst2.append(image)

    detector = htm.handDetector(detectionCon=0.5)
    fingerid = [4, 8, 12, 16, 20] # Tọa độ các đỉnh của từng ngón tay
    numberFingers = 0
    
    while True:
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame, draw=False) # Phát hiện vị trí

        if len(lmList) != 0:
            fingers = [] # Khởi tạo mảng lưu trạng thái 5 ngón tay

            # Xác định đây là tay trái hay tay phải (giả định lòng bàn tay hướng về camera)
            isRightHand = lmList[5][1] < lmList[17][1]

            # 1. Kiểm tra ngón cái
            if isRightHand:
                if lmList[fingerid[0]][1] < lmList[fingerid[0] - 1][1]:
                    fingers.append(1) # Mở
                else:
                    fingers.append(0) # Đóng
            else:
                if lmList[fingerid[0]][1] > lmList[fingerid[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # 2. Kiểm tra các ngón dài (trỏ, giữa, áp út, út)
            for id in range(1, 5):
                if lmList[fingerid[id]][2] < lmList[fingerid[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            # Tính tổng số ngón tay đang mở để hiển thị ảnh từ folder
            numberFingers = fingers.count(1)

            # 3. Chửi khi giơ ngón giữa
            if fingers == [0, 0, 1, 0, 0]:
                cv2.putText(frame, "Fuck you!", (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 3)

        # Phần hiển thị ảnh nhỏ ở góc trái (thêm check if để tránh lỗi IndexError nếu danh sách ảnh không đủ)
        if numberFingers < len(lst2):
            h, w, c = lst2[numberFingers].shape
            frame[0: h, 0: w] = lst2[numberFingers] 

        # Hiển thị số ngón tay
        cv2.putText(frame, str(numberFingers), (25, 450), cv2.FONT_ITALIC, 4, (255, 0, 0), 4)

        # Viết FPS: frame per second, số khung hình trên giây
        cTime = time.time() # Số giây, tính từ 0:0:0 ngày 1/1/1970
        fps = 1/(cTime - pTime)
        pTime = cTime

        # Hiển thị FPS
        cv2.putText(frame, f"FPS: {int(fps)}", (115, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)

        cv2.imshow("Count Fingers", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()