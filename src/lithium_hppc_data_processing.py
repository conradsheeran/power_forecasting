import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.signal import find_peaks
import sys
import math

def drawing_hppc_charts(file_path):
    """
    分析HPPC（混合脉冲功率特性）测试数据文件。

    该函数会加载指定的.mat文件，识别功率脉冲，计算每个脉冲的响应时间，
    并在控制台打印详细分析结果，最后生成一个可视化的功率曲线图。

    参数:
        file_path (str): 要分析的 .mat 文件的完整或相对路径。
    """
    print("\n" + "="*70)
    print(f"开始分析文件: {file_path}")

    power_threshold = 1.0   # (瓦) 高于此功率值才被认为是有效脉冲的开始
    min_peak_height = 5.0   # (瓦) 脉冲的最小峰值功率，以过滤掉噪声
    min_peak_distance = 50  # (数据点) 两个脉冲之间的最小距离，确保找到不同脉冲

    try:
        data = loadmat(file_path)['meas']
    except FileNotFoundError:
        print(f'错误：文件加载失败！文件 "{file_path}" 未找到', file=sys.stderr)
        return

    if 'Time' not in data.dtype.names or 'Power' not in data.dtype.names:
        print('错误：数据文件中缺少 "Time" 或 "Power" 字段，请检查文件内容', file=sys.stderr)
        return

    time_vec = data['Time'][0, 0].flatten()
    power_vec = np.abs(data['Power'][0, 0].flatten())  # 取功率绝对值

    sample_interval = np.mean(np.diff(time_vec))  # np.diff 计算相邻元素的差
    print(f'平均数据采样间隔为: {sample_interval:.3f} 秒')

    # 定位所有脉冲的峰值位置
    peak_locations, _ = find_peaks(power_vec, height=min_peak_height, distance=min_peak_distance)

    if peak_locations.size == 0:
        print('错误：在数据中未找到符合条件的功率脉冲', file=sys.stderr)
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

    print('\n===================================================================')
    print('                           脉冲结果')
    print('===================================================================')
    print(f'{"序号":<5s} {"目标功率 (W)":<18s} {"计算的响应时间 (s)":<22s} {"响应结果分析":<s}')
    print('-------------------------------------------------------------------')
    for i, (power, time) in enumerate(zip(target_powers, time_to_reach_power)):
        note = ''
        if time == 0:
            note = '响应发生在单个采样点内'
        print(f'{i+1:<5d} {power:<18.2f} {time:<22.4f} {note:<s}')
    print('-------------------------------------------------------------------\n')

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='w')

    ax.plot(time_vec, power_vec, color='#1a66cc', linewidth=1.5, label='功率曲线')  # 功率曲线
    ax.plot(time_vec[peak_locations], power_vec[peak_locations], 'o',
            markersize=5, markerfacecolor='red', markeredgecolor='black',
            linestyle='None', label='检测到的脉冲峰值')  # 峰值点

    plt.rcParams['font.sans-serif'] = ['SimHei', 'Heiti TC', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

    ax.set_title('HPPC 功率曲线', fontsize=12)
    ax.set_xlabel('时间 (s)', fontsize=10)
    ax.set_ylabel('功率 (w)', fontsize=10)
    ax.grid(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='upper left')

    plt.tight_layout()
    plt.show()