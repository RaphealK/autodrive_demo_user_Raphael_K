import contextlib
import os
import time

import config
from Done.vehicleControl import *
from socket_config import *

print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sceneInfoOutputGap = config.sceneInfoOutputGap


def straight_drive_algorithm(apiList, vehicleoControl):
    """

    :param apiList: 来自仿真环境的API数据。
    :param vehicleoControl: 车辆控制API对象。
    :return: 控制命令字典的JSON字符串。
    """
    desired_speed = 10
    current_position = apiList.DataGnssAPI()
    duishouche_position_list = apiList.ObstacleEntryListAPI()
    duishouche_position = duishouche_position_list[0]
    if 'velX' in duishouche_position:
        v1 = duishouche_position['velY']
    distance_traveled = (current_position['posX'] - duishouche_position['posX']) ** 2 + (
                current_position['posY'] - duishouche_position['posY']) ** 2
    print(
        f"  {distance_traveled}  {current_position['velX']}  {duishouche_position['velX']}  {duishouche_position['velY']}  {duishouche_position['velZ']}")
    if isinstance(duishouche_position['velX'], (int, float)):
        v1 = float(duishouche_position['velX'])
    if isinstance(current_position['velX'], (int, float)):
        v2 = float(current_position['velX'])
    if distance_traveled < v2 or v1 < 1 and distance_traveled < 8:
        vehicleoControl.__throttleSet__(throttle=0)
        vehicleoControl.__brakeSet__(1, speed=v2)
    elif distance_traveled > v2 * 2:
        vehicleoControl.__steeringSet__(steering=0)
        vehicleoControl.__throttleSet__(throttle=v1 * 1.2, speed=v2)
    else:
        vehicleoControl.__steeringSet__(steering=0)
        vehicleoControl.__throttleSet__(throttle=v1 * 0.95, speed=v2)
    control_command = json_encoder(vehicleoControl)
    return json.dumps(control_command)


def main():
    loop_counter = 0
    vehicleoControl1 = VehicleControlAPI(0, 0, 0)  # 控制初始化
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
                        control_dict_demo = straight_drive_algorithm(apiList, vehicleoControl1)

                        # 发送控制命令给仿真环境
                        socketServer.socket_send(control_dict_demo)

                loop_counter += 1


if __name__ == "__main__":
    main()
