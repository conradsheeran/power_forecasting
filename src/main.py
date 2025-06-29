import lithium_hppc_data_processing

file_path1 = "../data/Panasonic 18650PF Data/25degC/hppc.mat"
file_path2 = "../data/Panasonic 18650PF Data/0degC/hppc.mat"

dataloader1 = lithium_hppc_data_processing.DataLoader(file_path1)
dataloader2 = lithium_hppc_data_processing.DataLoader(file_path2)

lithium_hppc_data_processing.plot_hppc(dataloader1.load_hppc_data()[0], dataloader1.load_hppc_data()[1])
lithium_hppc_data_processing.plot_hppc(dataloader1.load_hppc_data()[0], dataloader2.load_hppc_data()[1])
