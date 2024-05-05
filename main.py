import contextlib
import math
import os
import time

import config
from Done.vehicleControl import *
from socket_config import *

print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sceneInfoOutputGap = config.sceneInfoOutputGap


def maintain_stop(apiList, vehicleoControl1):
    """
    在接近停止线时，保持速度和加速度为0，持续5秒。

    :param apiList: 来自仿真环境的API数据。
    :param vehicleoControl1: 车辆控制API对象。
    :return: 控制命令字典的JSON字符串。
    """
    # 获取当前车辆位置和偏航角
    current_position = apiList.DataGnssAPI()
    current_yaw = current_position['oriZ']

    # 初始化起点位置、目标偏航角和转向状态
    if not hasattr(vehicleoControl1, 'start_position_x'):
        vehicleoControl1.start_position_x = current_position['posX']
        vehicleoControl1.start_position_y = current_position['posY']
        vehicleoControl1.target_yaw = current_yaw + 90  # 假设初始右转90度
        vehicleoControl1.is_turning = False

    # 定义终点位置(场景测试得出)
    end_point_x = -135
    end_point_y = -30

    # 计算从起点行驶的距离和到终点的距离
    distance_traveled = calculate_distance(current_position['posX'], current_position['posY'],
                                           vehicleoControl1.start_position_x, vehicleoControl1.start_position_y)
    print(f'distance_traveled: {distance_traveled}')
    distance_to_end = calculate_distance(current_position['posX'], current_position['posY'],
                                         end_point_x, end_point_y)
    print(f'distance_to_end: {distance_to_end}')
    vehicleoControl1.__keyboardControl__()
    control_command = json_encoder(vehicleoControl1)
    return json.dumps(control_command)


def calculate_distance(x1, y1, x2, y2):
    """
    计算两点之间的距离。
    :param x1: 点 1 的 x 坐标。
    :param y1: 点 1 的 y 坐标。
    :param x2: 点 2 的 x 坐标。
    :param y2: 点 2 的 y 坐标。
    :return: 两点之间的距离。
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def main():
    loop_counter = 0
    vehicleoControl1 = VehicleControlAPI(0, 0, 0, 20)  # 控制初始化
    socketServer = SocketServer()
    socketServer.socket_connect()

    # 获取当前时间并格式化
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    filename = f"./Debug/debug_{current_time}.txt"

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
                        control_dict_demo = maintain_stop(apiList, vehicleoControl1)

                        # 发送控制命令给仿真环境
                        socketServer.socket_send(control_dict_demo)

                loop_counter += 1


if __name__ == "__main__":
    main()
