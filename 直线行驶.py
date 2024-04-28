import os

import config
from socket_config import *
from vehicleControl import *

print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sceneInfoOutputGap = config.sceneInfoOutputGap

import math

def straight_drive_algorithm(apiList, vehicleoControl):
    current_position = apiList.DataGnssAPI()

    if not hasattr(vehicleoControl, 'start_position_x'):
        vehicleoControl.start_position_x = current_position['posX']
        vehicleoControl.start_position_y = current_position['posY']

    distance_traveled = math.sqrt((current_position['posX'] - vehicleoControl.start_position_x) ** 2 +
                                   (current_position['posY'] - vehicleoControl.start_position_y) ** 2)

    if distance_traveled < 50:
        vehicleoControl.__steeringSet__(steering=0)
        vehicleoControl.__throttleSet__(throttle=1)
    else:
        vehicleoControl.__throttleSet__(throttle=0)
        vehicleoControl.__brakeSet__(brake=1)

    control_command = json_encoder(vehicleoControl)
    return json.dumps(control_command)


def main():
    loop_counter = 0
    vehicleoControl1 = vehicleoControlAPI(0, 0, 0)  # 控制初始化
    socketServer = SocketServer()
    socketServer.socket_connect()

    while True:
        dataState, apiList = socketServer.socket_launch()
        if dataState:
            if apiList != None:
                if loop_counter % sceneInfoOutputGap == 1:
                    print("\n\nInfo begin:")
                    apiList.showAllState()
                    print("gear mode: ", vehicleoControl1.gear)

        if dataState and loop_counter == 0:
            socketServer.socket_respond()

        elif dataState and apiList.messageState() and loop_counter != 0:
            # 调用直行算法函数，传入当前的apiList和vehicleoControl对象
            control_dict_demo = straight_drive_algorithm(apiList, vehicleoControl1)

            # 发送控制命令给仿真环境
            socketServer.socket_send(control_dict_demo)
        loop_counter += 1


if __name__ == "__main__":
    main()