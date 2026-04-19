import json


def openFile(file):
    with open(file, 'r') as file:
        envs = json.load(file)
        return envs


def saveSnSecret(key, value, env):
    # 读取 JSON 文件
    with open('sn.json', 'r') as file:
        data = json.load(file)
    # 修改现有的键值对（如果存在）
    if env in data:
        env_data = data[env]
        env_data[str(key)] = value
        # 写回文件
        with open('sn.json', 'w') as file:
            json.dump(data, file, indent=4)  # indent=4 用于美化格式


def getSnSecret(productModel, sn, env):
    key = f"{productModel}_{sn}"
    with open('sn.json', 'r') as file:
        data = json.load(file)
        if key in data[env]:
            return data[env][key]
        else:
            return None
