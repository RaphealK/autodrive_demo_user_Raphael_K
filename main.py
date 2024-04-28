import time
import math
import os
import contextlib
import sys
import json
import config
from socket_config import *
from vehicleControl import *

print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sceneInfoOutputGap = config.sceneInfoOutputGap

def maintain_stop(apiList, vehicleoControl1):
    """
    在接近停止线时，保持速度和加速度为0，持续5秒。

    :param apiList: 来自仿真环境的API数据。
    :param vehicleControl: 车辆控制API对象。
    :param current_time: 当前仿真时间。
    :return: 控制命令字典的JSON字符串。
    """
    # 假设停止线的位置信息
    control_command = json_encoder(vehicleoControl1)
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
                    if apiList != None:
                        if loop_counter % sceneInfoOutputGap == 1:
                            print("\n\nInfo begin:")
                            apiList.showAllState()
                            print("gear mode: ", vehicleoControl1.gear)

                if dataState and loop_counter == 0:
                    socketServer.socket_respond()

                elif dataState and apiList.messageState() and loop_counter != 0:
                    # 调用直行算法函数，传入当前的apiList和vehicleoControl对象
                    control_dict_demo = maintain_stop(apiList, vehicleoControl1)

                    # 发送控制命令给仿真环境
                    socketServer.socket_send(control_dict_demo)
                loop_counter += 1


if __name__ == "__main__":
    main()