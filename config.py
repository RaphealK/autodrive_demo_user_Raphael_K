# 调参专用文件
from math import cos, sin, tan, pi
import numpy as np

stateShowBool = True
# 显示动画
show_animation = True
# obstacle信息输出间隔
sceneInfoOutputGap = 2
# traffic light信息开关

# 车辆几何参数
Vehicle_Length = 3.0  # 车辆长度
Vehicle_Width = 2.0   # 车辆宽度
LF = 3.3  # 前后轮之间的距离
LB = 1.0  # 后轮到车尾的距离
MAX_STEER = pi/4  # [rad] 最大转向角

# 地图元素参数
XY_GRID_RESOLUTION = 2.0  # [m] XY平面栅格分辨率
YAW_GRID_RESOLUTION = np.deg2rad(5.0)  # [rad] 偏航角栅格分辨率

# 动力学参数
N_STEER = 20              # 转向命令数量
MOTION_RESOLUTION = 0.08  # [m] 路径插值分辨率

# 路径规划参数
SB_COST = 100.0          # 切换方向惩罚成本
BACK_COST = 50.0         # 后退惩罚成本
STEER_CHANGE_COST = 2.0  # 转向角变化惩罚成本
NON_STRAIGHT_COST = 0.0  # 非直行惩罚成本
H_COST = 3.0             # 启发式成本
M_COST = 3.0             # 成本地图系数

SB_COST = 100.0          # 切换方向惩罚成本
BACK_COST = 50.0         # 后退惩罚成本
STEER_CHANGE_COST = 2.0  # 转向角变化惩罚成本
STEER_COST = 0.0         # 非零转向角惩罚成本
H_COST = 2.5             # 启发式成本
