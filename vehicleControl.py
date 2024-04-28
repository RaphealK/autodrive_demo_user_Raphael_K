from pynput.keyboard import Key, Listener


class vehicleoControlAPI:
    # 初始化方法，设置车辆控制的初始状态
    def __init__(self, throttle, brake, steering):
        self.dirStr_ = None  # 方向字符串，暂未使用
        self.throttle = throttle  # 油门值
        self.brake = brake  # 刹车值
        self.steering = steering  # 转向角度
        self.handbrake = False  # 手刹状态
        self.isManualGear = False  # 是否为手动档，暂未使用
        self.gear = 3  # 档位，默认为3
        self.dir_ = None  # 实际方向，用于键盘控制模式
        self.pathlistx = []  # 轨迹x坐标列表
        self.pathlisty = []  # 轨迹y坐标列表

    # 设置油门方法，根据键盘模式与否调整相应的车辆控制逻辑
    def __throttleSet__(self, throttle, speed=0, keyboardModel=False):
        if keyboardModel:  # 如果是键盘模式
            if throttle >= 0:
                self.throttle = throttle
                self.brake = 0
        else:  # 非键盘模式，根据speed调整油门
            if throttle - speed > 0:
                self.throttle = throttle - speed
                print("throttle: ", self.throttle, speed, throttle)
                self.brake = 0

    # 设置刹车方法，逻辑与设置油门类似
    def __brakeSet__(self, brake, speed=0, keyboardModel=False):
        if keyboardModel:  # 键盘模式直接设置刹车值
            if brake >= 0:
                self.brake = brake
                self.throttle = 0
        else:  # 非键盘模式，根据speed调整刹车
            if brake - speed <= 0:
                self.brake = speed - brake
                print("brake: ", self.brake, speed, brake)
                self.throttle = 0

    # 设置转向角度方法，键盘模式下直接设置，非键盘模式则根据偏航角调整
    def __steeringSet__(self, steering, yaw=0, keyboardModel=False):
        if keyboardModel:
            self.steering = steering
        else:
            self.steering = steering - yaw
            print("steer: ", self.steering, steering, yaw)

    # 初始化键盘监听器，用于键盘控制模式
    def __listenerInit__(self, pressState, keyboardModel=False):
        listener = Listener(on_press=pressState)
        listener.start()
        listener.join()

    # 键盘控制方法，根据不同按键进行车辆控制
    def __keyboardControl__(self):

        def on_press(key):
            if key == Key.up:
                self.dir_ = "key_up"
                self.__throttleSet__(1, keyboardModel=True)
            elif key == Key.down:
                self.dir_ = "key_down"
                self.__brakeSet__(1, keyboardModel=True)
            elif key == Key.left:
                self.dir_ = "key_left"
                self.__steeringSet__(-0.1, keyboardModel=True)
            elif key == Key.right:
                self.dir_ = "key_right"
                self.__steeringSet__(0.1, keyboardModel=True)
            elif key == Key.enter:
                self.dir_ = "key_right"
                self.__brakeSet__(0, keyboardModel=True)

            return False  # 停止监听按键

        self.__listenerInit__(on_press)
        return self.dir_

    # 清除指令方法，将车辆恢复到默认状态
    def __instructClear__(self):
        self.throttle = 0
        self.brake = 100
        self.steering = 0

    # PID控制方法，暂为空实现
    def __PidControl__(self, trajList):
        pass

    # MPC控制方法，暂为空实现
    def __MPCControl__(self, trajList):
        pass


# JSON编码器，用于将车辆控制状态编码为JSON格式
def json_encoder(vehicleoControlAPI):
    control_dict = {"code": 4,  # 消息类型代码，这里固定为4
                    "UserInfo": None,
                    "SimCarMsg": {
                        "Simdata": "null",  # 模拟数据为null
                        "VehicleControl": {  # 车辆控制信息
                            "throttle": 1.0,
                            "brake": 1.0,
                            "steering": 1.0,
                            "handbrake": False,
                            "isManualGear": False,
                            "gear": 3
                        },
                        "Trajectory": None,  # 轨迹信息
                        "DataGnss": None,  # GNSS数据
                        "DataMainVehilce": None,  # 主车数据
                        "VehicleSignalLight": None,  # 信号灯状态
                        "ObstacleEntryList": [],  # 障碍物列表
                        "TrafficLightList": [],  # 交通灯列表
                        "RoadLineList": [],  # 路线列表
                        "DashboardMsg": {  # 仪表板消息
                            "x": [1.0, 2.0, 3.0],
                            "y": [1.0, 2.0, 3.0]
                        }
                    },
                    "messager": ""
                    }
    # 将车辆控制API的状态注入到JSON结构中
    control_dict["SimCarMsg"]["VehicleControl"]["throttle"] = vehicleoControlAPI.throttle
    control_dict["SimCarMsg"]["VehicleControl"]["brake"] = vehicleoControlAPI.brake
    control_dict["SimCarMsg"]["VehicleControl"]["steering"] = vehicleoControlAPI.steering
    control_dict["SimCarMsg"]["VehicleControl"]["handbrake"] = vehicleoControlAPI.handbrake
    control_dict["SimCarMsg"]["VehicleControl"]["isManualGear"] = vehicleoControlAPI.isManualGear
    control_dict["SimCarMsg"]["VehicleControl"]["gear"] = vehicleoControlAPI.gear
    control_dict["SimCarMsg"]["DashboardMsg"]["x"] = vehicleoControlAPI.pathlistx
    control_dict["SimCarMsg"]["DashboardMsg"]["y"] = vehicleoControlAPI.pathlisty
    return control_dict
