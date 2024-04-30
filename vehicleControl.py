from pynput.keyboard import Key, Listener


class VehicleControlAPI:
    def __init__(self, throttle, brake, steering, max_speed):
        self.dirStr_ = None
        self.throttle = throttle
        self.brake = brake
        self.steering = steering
        self.handbrake = False
        self.isManualGear = False
        self.gear = 3
        self.dir_ = None
        self.pathlistx = []
        self.pathlisty = []
        self.max_speed = max_speed  # 车辆的最大速度

    def __throttleSet__(self, throttle, speed=0, keyboardModel=False):
        normalized_speed = speed / self.max_speed  # 归一化速度值到 [0, 1]
        normalized_throttle = throttle  # 油门值已经在 [0, 1] 范围内

        if keyboardModel:  # throttle表示预期速度 speed表示当前速度
            if normalized_throttle >= 0:
                self.throttle = normalized_throttle
                self.brake = 0
        else:
            # 根据当前速度和期望的油门值调整油门
            if normalized_throttle > normalized_speed:
                self.throttle = normalized_throttle - normalized_speed
                self.brake = 0
            else:
                self.throttle = 0

        print("throttle: ", self.throttle, speed, throttle)

    def __brakeSet__(self, brake, speed=0, keyboardModel=False):
        normalized_speed = speed / self.max_speed  # 归一化速度值到 [0, 1]
        normalized_brake = brake  # 制动值已经在 [0, 1] 范围内

        if keyboardModel:
            if normalized_brake >= 0:
                self.brake = normalized_brake
                self.throttle = 0
        else:
            # 根据当前速度和期望的制动值调整制动
            if normalized_brake >= normalized_speed:
                self.brake = 1  # 应用最大制动力度
                self.throttle = 0
            else:
                self.brake = normalized_speed - normalized_brake
                self.throttle = 0

        print("brake: ", self.brake, speed, brake)

    def __steeringSet__(self, steering, yaw=0, keyboardModel=False):
        if keyboardModel:
            self.steering = steering
        else:
            self.steering = steering - yaw
            print("steer: ", self.steering, steering, yaw)

    def __listenerInit__(self, pressState, keyboardModel=False):
        listener = Listener(on_press=pressState)  # 创建监听器
        listener.start()  # 开始监听，每次获取一个键
        listener.join()  # 加入线程

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

            return False

        self.__listenerInit__(on_press)
        # print(self.dir_)
        return self.dir_

    def __instructClear__(self):
        self.throttle = 0
        self.brake = 100
        self.steering = 0
        pass

    def __PidControl__(self, trajList):
        # pid算法
        pass

    def __MPCControl__(self, trajList):
        # MPC算法
        pass


# 该文件暴露给外部
def json_encoder(vehicleoControlAPI):
    control_dict = {"code": 4,
                    "UserInfo": None,
                    "SimCarMsg": {
                        "Simdata": "null",
                        "VehicleControl": {
                            "throttle": 1.0,
                            "brake": 1.0,
                            "steering": 1.0,
                            "handbrake": False,
                            "isManualGear": False,
                            "gear": 3
                        },
                        "Trajectory": None,
                        "DataGnss": None,
                        "DataMainVehilce": None,
                        "VehicleSignalLight": None,
                        "ObstacleEntryList": [],
                        "TrafficLightList": [],
                        "RoadLineList": [],
                        "DashboardMsg": {
                            "x": [1.0, 2.0, 3.0],
                            "y": [1.0, 2.0, 3.0]
                        }
                    },
                    "messager": ""
                    }
    # throttle, brake, steering, handbrake, isManualGear, gear
    control_dict["SimCarMsg"]["VehicleControl"]["throttle"] = vehicleoControlAPI.throttle
    control_dict["SimCarMsg"]["VehicleControl"]["brake"] = vehicleoControlAPI.brake
    control_dict["SimCarMsg"]["VehicleControl"]["steering"] = vehicleoControlAPI.steering
    control_dict["SimCarMsg"]["VehicleControl"]["handbrake"] = vehicleoControlAPI.handbrake
    control_dict["SimCarMsg"]["VehicleControl"]["isManualGear"] = vehicleoControlAPI.isManualGear
    control_dict["SimCarMsg"]["VehicleControl"]["gear"] = vehicleoControlAPI.gear
    control_dict["SimCarMsg"]["DashboardMsg"]["x"] = vehicleoControlAPI.pathlistx
    control_dict["SimCarMsg"]["DashboardMsg"]["y"] = vehicleoControlAPI.pathlisty
    return control_dict