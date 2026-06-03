import cv2
import time
import numpy as np
import hand as htm
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

if __name__ == "__main__":
    pTime = 0
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector(detectionCon=0.5)
    
    devices = AudioUtilities.GetSpeakers()
    volume = devices.EndpointVolume.QueryInterface(IAudioEndpointVolume)
    volRange = volume.GetVolumeRange() # Phạm vi âm lượng
    minVol, maxVol = volRange[0], volRange[1]

    # Khởi tạo giá trị mặc định cho thanh âm lượng (khi chưa có tay)
    volBar = 400
    volPer = 0
    
    while True:
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame, draw=False) # Phát hiện vị trí

        if len(lmList) != 0:
            x1, y1, x2, y2 = lmList[4][1], lmList[4][2], lmList[8][1], lmList[8][2]
            cv2.circle(frame, (x1, y1), 10, (0, 225, 0), -1)
            cv2.circle(frame, (x2, y2), 10, (0, 225, 0), -1)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 225, 0), 3)
            cv2.circle(frame, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 225, 0), -1)
            length = math.hypot(x1 - x2, y1 - y2)
            minLen, maxLen = 25, 180
            if length < minLen:
                cv2.circle(frame, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 0, 255), -1)

            # Chuyển đổi khoảng cách (length) sang âm lượng của hệ thống
            vol = np.interp(length, [minLen, maxLen], [minVol, maxVol])
            # Chuyển đổi sang tọa độ thanh âm lượng và %
            volBar = np.interp(length, [minLen, maxLen], [400, 150]) # Trục Y ngược: 400 là đáy, 150 là đỉnh
            volPer = np.interp(length, [minLen, maxLen], [0, 100])   # Từ 0% đến 100%
            # Cài đặt âm lượng hệ thống
            volume.SetMasterVolumeLevel(vol, None)
        
        # Hiển thị âm lượng
        # 1. Vẽ viền ngoài của thanh âm lượng
        cv2.rectangle(frame, (50, 150), (85, 400), (0, 225, 0), 3)
        # 2. Vẽ phần được "đổ đầy" bên trong thanh âm lượng
        cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 225, 0), cv2.FILLED)
        # 3. Viết chữ phần trăm % ở dưới thanh âm lượng
        cv2.putText(frame, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 225, 0), 3)

        # Viết FPS: frame per second, số khung hình trên giây
        cTime = time.time() # Số giây, tính từ 0:0:0 ngày 1/1/1970
        fps = 1/(cTime - pTime)
        pTime = cTime

        # Hiển thị FPS
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 1)

        cv2.imshow("Volume", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()