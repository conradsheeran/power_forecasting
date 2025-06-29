import numpy as np
from scipy.io import loadmat
from scipy.signal import find_peaks
import sys
import matplotlib
matplotlib.use("qtagg")
import matplotlib.pyplot as plt

class DataLoader:
    def __init__(self, file_path: str):
        """
            初始化 DataLoader

            参数:
                file_path (str): 数据文件的路径
        """
        self.file_path = file_path

    def load_hppc_data(self):
        """
            加载 HPPC 数据。

            返回:
                time_vec 和 power_vec 的元组 (np.ndarray, np.ndarray)
        """
        try:
            data = loadmat(self.file_path)["meas"]
            print(f"已加载文件 \"{self.file_path}\"")
        except FileNotFoundError:
            raise FileNotFoundError(f"错误：\"{self.file_path}\" 未找到")
        except KeyError:
            raise KeyError(f"错误：\"{self.file_path}\" 中未找到结构体")

        if "Time" not in data.dtype.names or "Power" not in data.dtype.names:
            raise ValueError("错误：缺少 \"Time\" 或 \"Power\" 字段")

        time_vec = data["Time"][0, 0].flatten()
        power_vec = np.abs(data["Power"][0, 0].flatten())  # 取功率绝对值

        return time_vec, power_vec

def plot_hppc(time_vec, power_vec):
    """
        绘制 HPPC 功率曲线

        参数:
            time_vec (np.ndarray): 时间数据向量
            power_vec (np.ndarray): 功率数据向量
    """
    power_threshold = 1.0  # (瓦) 高于此功率值才被认为是有效脉冲的开始
    min_peak_height = 5.0  # (瓦) 脉冲的最小峰值功率，以过滤掉噪声
    min_peak_distance = 50  # (数据点) 两个脉冲之间的最小距离，确保找到不同脉冲

    sample_interval = np.mean(np.diff(time_vec))  # np.diff 计算相邻元素的差
    print(f"数据采样间隔为: {sample_interval:.3f} 秒")

    # 定位所有脉冲的峰值位置
    peak_locations, _ = find_peaks(power_vec, height=min_peak_height, distance=min_peak_distance)

    if peak_locations.size == 0:
        print("错误：未找到符合条件的功率脉冲", file=sys.stderr)
        return

    # 初始化结果存储列表
    target_powers = []
    time_to_reach_power = []

    # 分析每个脉冲并计算响应时间
    for loc in peak_locations:
        target_powers.append(power_vec[loc])

        # 从峰值向前搜索，找到脉冲的起始点
        start_index = loc
        while start_index > 0 and power_vec[start_index - 1] > power_threshold:
            start_index -= 1

        # 计算到达峰值功率所需的时间
        response_time = time_vec[loc] - time_vec[start_index]
        time_to_reach_power.append(response_time)

    print("\n===================================================================")
    print("                           脉冲结果")
    print("===================================================================")
    print(f"{'序号':<5s} {'目标功率 (W)':<18s} {'计算的响应时间 (s)':<22s} {'响应结果分析':<s}")
    print("-------------------------------------------------------------------")
    for i, (power, time) in enumerate(zip(target_powers, time_to_reach_power)):
        note = ""
        if time == 0:
            note = "响应发生在单个采样点内"
        print(f"{i + 1:<5d} {power:<18.2f} {time:<22.4f} {note:<s}")
    print("-------------------------------------------------------------------\n")

    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="w")

    ax.plot(time_vec, power_vec, color="#1a66cc", linewidth=1.5, label="功率曲线")  # 功率曲线
    ax.plot(time_vec[peak_locations], power_vec[peak_locations], "o",
            markersize=5, markerfacecolor="red", markeredgecolor="black",
            linestyle="None", label="检测到的脉冲峰值")  # 峰值点

    plt.rcParams["font.sans-serif"] = ["SimHei", "Heiti TC", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False

    ax.set_title("HPPC 功率曲线", fontsize=12)
    ax.set_xlabel("时间 (s)", fontsize=10)
    ax.set_ylabel("功率 (w)", fontsize=10)
    ax.grid(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left")

    plt.tight_layout()
    plt.show()