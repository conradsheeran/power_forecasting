# power_forecasting

## 1. 环境搭建

```bash
conda env create -f env.yml
conda activate power_forecasting
```

## 2. 目录结构

```bash
|-- LICENSE
|-- README.md
|-- data                   # 数据目录
|       `-- Panasonic 18650PF Data
|-- env.yml                # 环境配置文件
|-- src                    # 源代码目录
|       `-- main.py
         -- lithium_hppc_data_processing.py
`-- tmp                    # 临时文件目录
        `-- tmp.py
```

## 3. 注意事项

1. 环境搭建时执行完命令必须等一会，等待 Pycharm 建立索引
2. data 目录下不要存放大文件，影响 Git 速率
3. 不要修改 .gitignore 文件