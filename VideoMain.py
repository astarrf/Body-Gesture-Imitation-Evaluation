import cv2
import mediapipe as mp
# import time
from score import cal_score

mpDraw = mp.solutions.drawing_utils  # 通用绘图
mpPose = mp.solutions.pose  # pose的api
pose = mpPose.Pose()  # 函数实例化,按默认值传参数
cap = cv2.VideoCapture(0)  # 读取视频
# pTime = 0


def getVideoFrame():
    global results
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)  # 同hands.process(), 识别到的信息存入results
    # print(results.pose_landmarks)
    if results.pose_landmarks:
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        #print("Score: %d" % score)
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, _ = img.shape
            # print(id, lm)  # 把每一个检测点打印出来
            cx, cy = int(lm.x * w), int(lm.y * h)  # 相对坐标转换成实际坐标
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)  # 蓝色画点 BGR
    return cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    # cTime = time.time()
    # fps = 1 / (cTime - pTime)  # 计算帧率
    # pTime = cTime
    # cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)  # 左上角显示fps
    #cv2.imshow("Image", img)
    #if cv2.waitKey(5) == ord('q'):  # 每帧图像显示20ms，等待用户按下空格键退出
    #    break
#cap.release()
#cv2.destroyAllWindows()
# cv2.waitKey(1)  # mac用户需要添加


def getScore(img):
    score=0
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results_tar = pose.process(imgRGB)  # 同hands.process(), 识别到的信息存入results
    if results_tar.pose_landmarks and results.pose_landmarks:
        score = cal_score(list(results.pose_landmarks.landmark), list(results_tar.pose_landmarks.landmark))
        print(score)
    else:
        print('Fail to get gesture')
    return score

def finalize():
    cap.release()