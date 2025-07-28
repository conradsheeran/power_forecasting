import airsim
import time
import numpy as np
# import csv
# import os

DRONE_MASS = 1.2 # 模拟载重 (settings.json 中的 "Mass" 字段)
GRAVITY = 9.81 # 重力加速度
P_BASE = 150.0 # 基础功率
K_INDUCED = 0.08 # 诱导功率系数
K_PARASITIC = 0.12 # 寄生功率系数

FLIGHT_PATH = [
    airsim.Vector3r(20, 0, -10),
    airsim.Vector3r(20, 20, -10),
    airsim.Vector3r(0, 20, -10),
    airsim.Vector3r(0, 0, -10)
] # 飞行路径
FLIGHT_SPEED = 5 # 飞行速度
OUTPUT_FILENAME = '../airsim/results/airsim_power_simulation.csv'

def calculate_power(state: airsim.MultirotorState, mass: float) -> dict:
    """
        计算瞬时功率

        参数:
            state: 从 AirSim 获取的无人机状态对象
            mass: 无人机的总质量

        返回值:
            dict: 推力、各部分功率和总功率
    """
    # 从状态对象中获取线速度和线加速度向量
    velocity_vec = state.kinematics_estimated.linear_velocity
    acceleration_vec = state.kinematics_estimated.linear_acceleration

    # 计算标量速度值
    speed = np.linalg.norm([velocity_vec.x_val, velocity_vec.y_val, velocity_vec.z_val])
    thrust = mass * (GRAVITY - acceleration_vec.z_val)
    if thrust < 0:
        thrust = 0

    power_induced = K_INDUCED * np.power(thrust, 1.5) # 诱导功率
    power_parasitic = K_PARASITIC * np.power(speed, 3) # 寄生功率
    total_power = P_BASE + power_induced + power_parasitic # 总功率

    return {
        "thrust": thrust,
        "power_induced": power_induced,
        "power_parasitic": power_parasitic,
        "total_power": total_power
    }


def run_simulation_scenario(client: airsim.MultirotorClient, csv_writer, wind_vector: airsim.Vector3r):
    """
        仿真场景

        参数:
            client: AirSim 实例
            csv_writer: CSV 写入对象
            wind_vector: 风速向量 (x, y, z)
    """
    wind_desc = f"Wind (X:{wind_vector.x_val}, Y:{wind_vector.y_val}, Z:{wind_vector.z_val})"
    print(f"\n{'=' * 20}\n[SCENARIO START] {wind_desc}\n{'=' * 20}")

    # 重置
    client.reset()
    client.enableApiControl(True)
    client.armDisarm(True)

    # 设置风速
    if hasattr(client, 'simSetWind'):
        client.simSetWind(wind_vector)
    elif hasattr(client, 'setWind'):
        client.setWind(wind_vector)
    else:
        print("Warning: 无法找到设置风速的函数。将在无风环境下运行。")

    # 起飞
    print("-------------- 起飞 --------------")
    client.takeoffAsync().join()

    # 检查是否起飞
    if client.getMultirotorState().landed_state == airsim.LandedState.Landed:
        print("[Error] 起飞失败，正在重试...")
        client.takeoffAsync().join()
        time.sleep(1)

    print(f"-------------- 上升到 {-FLIGHT_PATH[0].z_val} 米 --------------")
    client.moveToZAsync(FLIGHT_PATH[0].z_val, FLIGHT_SPEED).join()
    time.sleep(2) # 悬停稳定

    # 执行预设航线
    for i, target_pos in enumerate(FLIGHT_PATH):
        print(f"--> 飞往航点 {i + 1}: ({target_pos.x_val}, {target_pos.y_val}, {target_pos.z_val})")
        client.moveToPositionAsync(
            target_pos.x_val, target_pos.y_val, target_pos.z_val, FLIGHT_SPEED,
            drivetrain=airsim.DrivetrainType.ForwardOnly,
            yaw_mode=airsim.YawMode(is_rate=False)
        ).join()
        print(f"    已到达航点 {i + 1}")
        start_time = time.time()
        while time.time() - start_time < 3:
            state = client.getMultirotorState()
            power_data = calculate_power(state, DRONE_MASS) # 计算功率
            kinematics = state.kinematics_estimated
            vel = kinematics.linear_velocity
            acc = kinematics.linear_acceleration
            pos = kinematics.position
            speed = np.linalg.norm([vel.x_val, vel.y_val, vel.z_val])

            # 写入 CSV 文件
            csv_writer.writerow([
                time.time(), # 时间戳
                wind_vector.x_val, wind_vector.y_val, wind_vector.z_val, # 风速
                DRONE_MASS, # 质量
                pos.x_val, pos.y_val, pos.z_val, # 位置
                vel.x_val, vel.y_val, vel.z_val, speed, # 速度
                acc.x_val, acc.y_val, acc.z_val, # 加速度
                power_data['thrust'], # 推力
                power_data['power_induced'], power_data['power_parasitic'], power_data['total_power'] # 功率
            ])

            time.sleep(0.1)

    print(f"[SCENARIO FINISHED] {wind_desc}")

# if __name__ == "__main__":
#     # 初始化 AirSim 实例
#     airsim_client = airsim.MultirotorClient()
#     airsim_client.confirmConnection()
#
#     # 定义风速
#     wind_scenarios = {
#         "无风": airsim.Vector3r(0, 0, 0),
#         "低速侧风 (2m/s, 右侧)": airsim.Vector3r(0, 2, 0),
#         "高速侧风 (5m/s, 右侧)": airsim.Vector3r(0, 5, 0),
#         "低速逆风 (2m/s, 前方)": airsim.Vector3r(2, 0, 0),
#         "高速逆风 (5m/s, 前方)": airsim.Vector3r(5, 0, 0),
#         "高速斜向风 (3m/s, 右前方)": airsim.Vector3r(3, 3, 0),
#     }
#
#     os.makedirs(os.path.dirname(OUTPUT_FILENAME), exist_ok=True)
#     with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             'timestamp', 'wind_x', 'wind_y', 'wind_z', 'drone_mass',
#             'pos_x', 'pos_y', 'pos_z',
#             'vel_x', 'vel_y', 'vel_z', 'speed',
#             'acc_x', 'acc_y', 'acc_z',
#             'thrust', 'power_induced', 'power_parasitic', 'total_power'
#         ]) # 写入 CSV 表头
#         for name, wind_vec in wind_scenarios.items():
#             run_simulation_scenario(airsim_client, writer, wind_vec)
#
#     airsim_client.reset()
#     airsim_client.armDisarm(False)
#     airsim_client.enableApiControl(False)