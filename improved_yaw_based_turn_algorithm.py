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


def improved_yaw_based_turn_algorithm(apilist, vehiclecontrol):
    """
    根据偏航角和预先定义的路况信息进行转弯,行驶到终点。
    :param apilist: 来自仿真环境的API数据。
    :param vehiclecontrol: 车辆控制API对象。
    :return: 控制命令字典的JSON字符串。
    """
    desired_speed = 10
    yaw_error_threshold = 3  # 偏航角误差阈值,小于该值时退出转弯状态
    straight_distance_threshold = 8  # 直行距离阈值

    # 获取当前车辆位置和偏航角
    current_position = apilist.DataGnssAPI()
    current_yaw = current_position['oriZ']

    # 初始化起点位置、目标偏航角和转向状态
    if not hasattr(vehiclecontrol, 'start_position_x'):
        vehiclecontrol.start_position_x = current_position['posX']
        vehiclecontrol.start_position_y = current_position['posY']
        vehiclecontrol.target_yaw = current_yaw + 180  # 假设初始右转90度
        vehiclecontrol.is_turning = False

    # 定义终点位置(场景测试得出)
    end_point_x = -135
    end_point_y = 100

    # 计算从起点行驶的距离和到终点的距离
    distance_traveled = calculate_distance(current_position['posX'], current_position['posY'],
                                           vehiclecontrol.start_position_x, vehiclecontrol.start_position_y)
    print(f'------distance_traveled: {distance_traveled}-----')
    distance_to_end = calculate_distance(current_position['posX'], current_position['posY'],
                                         end_point_x, end_point_y)
    print(f'-----distance_to_end: {distance_to_end}-----')

    # 判断是否到达终点
    if distance_to_end < 5:
        # 停止车辆
        vehiclecontrol.__brakeSet__(1)
    else:
        turn_points = [
            {'distance': 20, 'target_yaw': -148},  # 第一个转弯点：距离起点 28 米,目标偏航角 180 度
            {'distance': 35, 'target_yaw': -148},  # 第二个转弯点：距离起点 56 米,目标偏航角 270 度
            # ... 添加更多转弯点
        ]

        # 找到当前需要参考的转弯点
        current_turn_point = None
        for turn_point in turn_points:
            if distance_traveled > turn_point['distance']:
                current_turn_point = turn_point

        if current_turn_point:
            # 更新目标偏航角
            vehiclecontrol.target_yaw = current_turn_point['target_yaw']

            # 计算目标转向角
            yaw_error = vehiclecontrol.target_yaw - current_yaw
            # 将 yaw_error 限制在 [-180, 180] 范围内
            while yaw_error > 180:
                yaw_error -= 360
            while yaw_error < -180:
                yaw_error += 360

            # 计算转向角
            vehicle_length = 4.814
            turn_angle = math.atan(vehicle_length / 3) * yaw_error / 90
            # 将转向角限制在合理范围内 (例如 [-45°, 45°])
            turn_angle = max(-math.pi, min(turn_angle, math.pi))

            print(f'turn angle: {turn_angle}')
            print(f'yaw_error: {yaw_error}')

            # 判断是否需要进入或退出转弯状态
            if abs(yaw_error) > yaw_error_threshold:
                if not vehiclecontrol.is_turning:
                    # 开始转弯
                    vehiclecontrol.is_turning = True
                    print('正在转弯！！！')

                # 应用转向角进行转弯
                vehiclecontrol.__steeringSet__(steering=turn_angle)
                vehiclecontrol.__throttleSet__(throttle=desired_speed * 0.25, speed=current_position['velX'])
            else:
                if vehiclecontrol.is_turning:
                    # 退出转弯状态
                    vehiclecontrol.is_turning = False
                    print('退出转弯状态,开始直行！')

                # 直行
                vehiclecontrol.__steeringSet__(steering=0)
                vehiclecontrol.__throttleSet__(throttle=desired_speed, speed=current_position['velX'])
        else:
            # 检查是否需要进行直行
            straight_distance = distance_traveled - turn_points[-1]['distance']
            if straight_distance >= straight_distance_threshold:
                # 转弯后的直行
                vehiclecontrol.__steeringSet__(steering=0)
                vehiclecontrol.__throttleSet__(throttle=desired_speed * 0.25, speed=current_position['velX'])
            else:
                # 转弯前的直行
                vehiclecontrol.__steeringSet__(steering=0)
                vehiclecontrol.__throttleSet__(throttle=desired_speed, speed=current_position['velX'])

    # 将控制命令编码为JSON
    control_command = json_encoder(vehiclecontrol)
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
    vehicleo_control1 = VehicleControlAPI(0, 0, 0, 20)  # 控制初始化
    socket_server = SocketServer()
    socket_server.socket_connect()

    # 获取当前时间并格式化
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    filename = f"./Debug/debug_{current_time}.txt"

    with open(filename, "a", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            while True:
                data_state, api_list = socket_server.socket_launch()

                if data_state:
                    if api_list is not None:
                        if loop_counter % sceneInfoOutputGap == 1:
                            print("\n\nInfo begin:")
                            api_list.showAllState()
                            print("gear mode: ", vehicleo_control1.gear)

                    if loop_counter == 0:
                        socket_server.socket_respond()

                    elif api_list.messageState() and loop_counter != 0:
                        control_dict_demo = improved_yaw_based_turn_algorithm(api_list, vehicleo_control1)

                        # 发送控制命令给仿真环境
                        socket_server.socket_send(control_dict_demo)

                loop_counter += 1


if __name__ == "__main__":
    main()
