import lithium_hppc_data_processing

file_path1 = "../data/Panasonic 18650PF Data/25degC/hppc.mat"
file_path2 = "../data/Panasonic 18650PF Data/0degC/hppc.mat"

lithium_hppc_data_processing.drawing_hppc_charts(file_path1)
lithium_hppc_data_processing.drawing_hppc_charts(file_path2)
