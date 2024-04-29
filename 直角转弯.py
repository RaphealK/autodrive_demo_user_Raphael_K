import contextlib
import math
import os
import time

import config
from socket_config import *
from vehicleControl import *

print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sceneInfoOutputGap = config.sceneInfoOutputGap


def yaw_based_turn_algorithm(apiList, vehicleoControl):
    """
    直行并执行 3 米曲率的直角转弯，根据偏航角调整转向角。

    :param apiList: 来自仿真环境的API数据。
    :param vehicleoControl: 车辆控制API对象。
    :return: 控制命令字典的JSON字符串。
    """
    # 直行时的期望速度
    desired_speed = 10

    # 获取当前车辆位置和偏航角
    current_position = apiList.DataGnssAPI()
    current_yaw = current_position['oriZ']  # 获取当前偏航角

    # 初始化起点位置、目标偏航角和转向状态
    if not hasattr(vehicleoControl, 'start_position_x'):
        vehicleoControl.start_position_x = current_position['posX']
        vehicleoControl.start_position_y = current_position['posY']
        vehicleoControl.target_yaw = current_yaw + 90  # 假设右转90度
        vehicleoControl.is_turning = False

    # 计算从起点行驶的距离
    distance_traveled = math.sqrt((current_position['posX'] - vehicleoControl.start_position_x) ** 2 +
                                   (current_position['posY'] - vehicleoControl.start_position_y) ** 2)

    # 定义转弯点距离
    turning_point_distance = 28

    if distance_traveled < turning_point_distance:
        # 转弯前的直行
        vehicleoControl.__steeringSet__(steering=0)
        vehicleoControl.__throttleSet__(throttle=desired_speed, speed=current_position['velX'])
    else:
        if not vehicleoControl.is_turning:
            # 开始转弯
            vehicleoControl.is_turning = True

        # 计算目标转向角
        yaw_error = vehicleoControl.target_yaw - current_yaw
        # 将 yaw_error 限制在 [-180, 180] 范围内
        while yaw_error > 180:
            yaw_error -= 360
        while yaw_error < -180:
            yaw_error += 360
        vehicle_length = 4.814
        turn_angle = math.atan(vehicle_length / 3) * yaw_error / 90
        # 将转向角限制在合理范围内 (例如 [-45°, 45°])
        turn_angle = max(-math.pi/4, min(turn_angle, math.pi/4))

        # 应用转向角进行转弯
        vehicleoControl.__steeringSet__(steering=turn_angle)
        vehicleoControl.__throttleSet__(throttle=desired_speed * 0.5, speed=current_position['velX'])

    # 将控制命令编码为JSON
    control_command = json_encoder(vehicleoControl)
    return json.dumps(control_command)


def main():
    loop_counter = 0
    vehicleoControl1 = vehicleoControlAPI(0, 0, 0)  # 控制初始化
    socketServer = SocketServer()
    socketServer.socket_connect()

    # 获取当前时间并格式化
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    filename = f"debug_{current_time}.txt"

    with open(filename, "a", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            while True:
                dataState, apiList = socketServer.socket_launch()

                if dataState:
                    if apiList is not None:
                        if loop_counter % sceneInfoOutputGap == 1:
                            print("\n\nInfo begin:")
                            apiList.showAllState()
                            print("gear mode: ", vehicleoControl1.gear)

                    if loop_counter == 0:
                        socketServer.socket_respond()

                    elif apiList.messageState() and loop_counter != 0:
                        # 调用直行算法函数，传入当前的apiList和vehicleoControl对象
                        control_dict_demo = yaw_based_turn_algorithm(apiList, vehicleoControl1)

                        # 发送控制命令给仿真环境
                        socketServer.socket_send(control_dict_demo)

                loop_counter += 1


if __name__ == "__main__":
    main()
