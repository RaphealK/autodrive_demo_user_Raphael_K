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


def follow_vehicle_pid(api_list, vehicle_control):
    """
    :param api_list: 来自仿真环境的API数据。
    :param vehicle_control: 车辆控制API对象。
    :return: 控制命令字典的JSON字符串。
    """
    # 目标车距
    target_distance = 5

    # 获取主车GNSS数据
    main_vehicle_gnss = api_list.DataGnssAPI()
    main_vehicle_speed = int(float(main_vehicle_gnss['velX']))

    # 获取障碍物列表
    front_vehicle_gnss_list = api_list.ObstacleEntryListAPI()

    # 初始化前车GNSS数据为None，以防列表为空
    front_vehicle_gnss = None
    front_vehicle_gnss_speed = 0

    # 遍历障碍物列表，查找第一个障碍物
    for id in front_vehicle_gnss_list:
        front_vehicle_gnss = id
        # front_vehicle_gnss_speed = int(float(id['velX']))
        print(front_vehicle_gnss)
        break

    # 如果没有找到障碍物，front_vehicle_gnss将保持None，可以在这里添加处理逻辑
    if front_vehicle_gnss is None:
        print("没有检测到障碍物")
    else:
        # 处理检测到障碍物的逻辑
        print(f"检测到障碍物，速度: {front_vehicle_gnss_speed}")
    print(front_vehicle_gnss_list)
    print(main_vehicle_speed)

    # 计算主车与前车的距离
    delta_pos_x = int(main_vehicle_gnss['posX']) - int(front_vehicle_gnss['posX'])
    delta_pos_y = int(main_vehicle_gnss['posY']) - int(front_vehicle_gnss['posY'])
    distance_traveled = int(math.sqrt(delta_pos_x ** 2 + delta_pos_y ** 2))
    print(f'distance_traveled: {distance_traveled}')

    # 根据距离调整油门或刹车
    if distance_traveled < target_distance + 2:
        # vehicle_control.__throttleSet__(throttle=0)
        vehicle_control.__brakeSet__(brake=1)
        print(f'distance_traveled: {distance_traveled}')
        print('开始刹车')
    elif distance_traveled > 5:
        # vehicle_control.__brakeSet__(brake=0)
        vehicle_control.__throttleSet__(throttle=0.6, speed=front_vehicle_gnss_speed * 1.2)
        print(f'distance_traveled: {distance_traveled}')
        print('加速追赶')
    else:
        vehicle_control.__throttleSet__(throttle=1, speed=main_vehicle_speed)
        # vehicle_control.__brakeSet__(brake=1, speed=main_vehicle_speed)
        print(f'distance_traveled: {distance_traveled}')
        print('状态保持当前速度')

    # 编码控制指令
    control_command = json_encoder(vehicle_control)
    return json.dumps(control_command)


def main():
    loop_counter = 0
    vehicleo_control = VehicleControlAPI(0, 0, 0, 20)  # 控制初始化
    socket_server = SocketServer()
    socket_server.socket_connect()

    # 获取当前时间并格式化
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    filename = f"debug_{current_time}.txt"

    with open(filename, "a", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            while True:
                data_state, api_list = socket_server.socket_launch()

                if data_state:
                    if api_list is not None:
                        if loop_counter % sceneInfoOutputGap == 1:
                            print("\n\nInfo begin:")
                            api_list.showAllState()
                            print("gear mode: ", vehicleo_control.gear)

                    if loop_counter == 0:
                        socket_server.socket_respond()

                    elif api_list.messageState() and loop_counter != 0:
                        # 调用直行算法函数，传入当前的apiList和vehicleoControl对象
                        control_dict_demo = follow_vehicle_pid(api_list, vehicleo_control)

                        # 发送控制命令给仿真环境
                        socket_server.socket_send(control_dict_demo)

                loop_counter += 1


if __name__ == "__main__":
    main()
