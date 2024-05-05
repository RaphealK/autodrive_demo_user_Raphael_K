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
    desired_speed = 10

    current_position = apiList.DataGnssAPI()
    duishouche_position_list = apiList.ObstacleEntryListAPI()
    if not hasattr(vehicleoControl, 'start_position_x'):
        vehicleoControl.start_position_x = current_position['posX']
        vehicleoControl.start_position_y = current_position['posY']
    if duishouche_position_list and isinstance(duishouche_position_list[0], dict):
        duishouche_position = duishouche_position_list[0]
        if 'posY' in duishouche_position and duishouche_position['posY'] - current_position['posY'] > -6:
            vehicleoControl.__brakeSet__(1, 2)
    print(f"1:{duishouche_position['posY'] - current_position['posY']}!!!")
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
