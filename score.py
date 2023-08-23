# 夹角（正面视角，与水平面的角度）：16-14，14-12，12-11，11-13，13-15，24-23，24-26，26-28，23-25，25-27
# Z坐标（不确定效果会不会好因为这个本来就是估测值）：与臀部平面的距离
# 可以检测手脚四点的z值，与四肢长度做比值，作为一个评测点
# visibility 需要设置一个阈值，低于这个阈值说明这个点看不见检测不到，不能使用（0-1）
# 注意需要评测图像与目标图像【比例一致】才能进行计算
# 注意需要目标图像将关键点11、12、13、14、15、16、23、24、25、26、27、28全都拍到才能进行计算

import math

VISI_THRESHOLD = 0.8    # 认为该点可见的阈值，需要调参
XY_SCORE_WEIGHT = [16, 16, 16, 16, 16, 16, 16, 16, 16, 16]      # 正视图的各组点分数权值，需要调参
XY_POINT_LIST = [(16, 14), (14, 12), (12, 11), (11, 13), (13, 15), (24, 23), (24, 26), (26, 28), (23, 25), (25, 27)]
Z_SCORE_WEIGHT = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]      # Z值（与臀部平面的距离）的各点分数权值，需要调参
Z_POINT_LIST = [11, 12, 13, 14, 15, 16, 25, 26, 27, 28]


def cal_angle(x1, y1, x2, y2):
    """

    :param x1, y1: the first point coordinate
    :param x2, y2:  the second point coordinate
    :return: the angle of p1-p2 with the horizontal
    """
    return math.atan2(y1 - y2, x1 - x2)


def cal_score(landmark, landmark_tar):
    """

    :param landmark: the landmark of captured image, list(results.pose_landmarks.landmark)
    :param landmark_tar: the landmark of target image, list(results.pose_landmarks.landmark)
    :return: score
    """

    # 计算正视图四肢夹角的部分分数，满分80
    xy_score = 80
    for idx, (p1, p2) in enumerate(XY_POINT_LIST):
        if landmark[p1].visibility >= VISI_THRESHOLD and landmark[p2].visibility > VISI_THRESHOLD and landmark_tar[p1].visibility >= VISI_THRESHOLD and landmark_tar[p2].visibility >= VISI_THRESHOLD:
            angle = cal_angle(landmark[p1].x, landmark[p1].y, landmark[p2].x, landmark[p2].y)
            angle_tar = cal_angle(landmark_tar[p1].x, landmark_tar[p1].y, landmark_tar[p2].x, landmark_tar[p2].y)
            xy_score -= abs(angle-angle_tar) / angle_tar * XY_SCORE_WEIGHT[idx]
        else:
            xy_score -= 8

    # 计算四肢与与臀部平面的距离部分分数, 满分20
    z_score = 20
    for idx, p in enumerate(Z_POINT_LIST):
        if landmark[p].visibility >= VISI_THRESHOLD and landmark_tar[p].visibility >= VISI_THRESHOLD:
            z_score -= abs(landmark[p].z-landmark_tar[p].z) / landmark_tar[p].z * Z_SCORE_WEIGHT[idx]
        else:
            z_score -= 2

    # 计算总分，不出现负分
    score = max(z_score, 0) + max(xy_score, 0)

    return score
