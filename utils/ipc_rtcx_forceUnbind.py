import json

import ipc_db
from AESUtil import AESUtil
import rtcxUtil
import uuid
from ipc_rtcx_login import RTCXLogin
import datetime

baseData = {
    "id": str(uuid.uuid4()),
    "params": {},
    "request": {
        "apiVer": "1.0.0"
    },
    "version": "1.0"
}

product = ["event_1_year", "continuous_1_year","event_1_year_lens3","continuous_1_year_lens3"]
envs = ["dev", "test", "dvt"]
key = "gh&*$P3124334343"
openIdAppKey = "JaLezS0jUtdcgOduHMgenKfUr"

models = {
    "010001": "ID500 Pro",
    "010002": "OD600 Pro",
    "010004": "ID500 Plus",
    "010003": "D500"
}

status_map = {
    0: "有效(使用中)",
    1: "无效(已过期)",
    2: "冻结(停用)"
}

rtcx = {
    "ces": "https://third-gateway.iotrtcus.com",
    "dvt": "https://third-gateway.iotrtc.cn",
    "dev": "https://third-gateway.iotrtc.cn",
    "test": "https://third-gateway.iotrtc.cn"
}


class Rtcx:

    def __init__(self, env):
        self.env = env
        self.rtcx_url = rtcx[self.env]

    # 相速购买接口
    def buy(self, iotId, openId):
        for specification in product:
            params = {
                "iotId": iotId,
                "userName": openId,
                "specification": specification,
                "copies": "1",
                "immediateUse": "true"
            }
            path = "/platform/customer/cloudstorage/commodity/buy"
            baseData["params"] = params
            result = rtcxUtil.request(path, baseData, self.rtcx_url)
            print(f"购买：{specification}，结果是：{result}")

    # 相速解绑接口
    def unbind(self, iotId, openId):
        params = {
            "openId": openId,
            "openIdAppKey": openIdAppKey,
            "iotId": iotId
        }
        path = "/platform/cloud/user/device/unbind"
        baseData["params"] = params
        result = rtcxUtil.request(path, baseData,self.rtcx_url)
        print(f"解绑：{iotId} 用户：{openId}，结果是：{result}")

    def getIotBuy(self, iotId):
        params = {
            "iotId": iotId
        }
        path = "/platform/vision/customer/cloudstorage/order/query"
        baseData["params"] = params
        baseData["params"] = params
        result = rtcxUtil.request(path, baseData, self.rtcx_url)
        result = json.loads(result)
        if result["code"] == 200:
            if result.get("data") and result["data"].get("orderList"):
                for order in result["data"]["orderList"]:
                    recordType = order.get("recordType")
                    status = order.get("status")
                    specification = order.get("specification", "")
                    status_desc = status_map.get(status, f"未知状态({status})")

                    # 判断类型
                    if specification.startswith("event") or recordType == 2:
                        log_type = "事件型套餐"
                    elif specification.startswith("continuous") or recordType == 1:
                        log_type = "云存储套餐"
                    else:
                        log_type = "未知套餐"

                    # 打印日志
                    if recordType == 1:
                        endTime = order.get("endTime")
                        endTime_str = datetime.datetime.fromtimestamp(endTime / 1000).strftime(
                            "%Y-%m-%d %H:%M:%S") if endTime else "无到期时间"
                        print(
                            f"[设备:{iotId}] {log_type} | 规格:{specification} | 状态:{status_desc} | 到期时间:{endTime_str} | recordType:{recordType}")
                    elif recordType == 2:
                        print(
                            f"[设备:{iotId}] {log_type} | 规格:{specification} | 状态:{status_desc} | recordType:{recordType}")

    # 通过账号 购买运存
    def buyBuyPhone(self, phone):
        phonex = AESUtil.encrypt(key, phone)
        sql = f"select user_id from user where status = 1 and user_mobile = '{phonex}' and destroy_status = 1"
        if self.env == "ces":
            sql = f"select user_id from user where status = 1 and user_mail = '{phonex}' and destroy_status = 1"
        database = "ugreen_dpt_user_" + self.env
        db = ipc_db.DB(self.env, database)
        data = db.select(sql)
        if data and len(data) > 0:
            userId = data[0]["user_id"]
            database = "ugreen_dpt_" + self.env
            sqlx = f"select iot_id,open_id,sn,product_serial_no from ipc_bind_record where status = 1 and bind_type = 0 and  user_id = '{userId}'"
            db = ipc_db.DB(self.env, database)
            rows = db.select(sqlx)
            if rows and len(rows) > 0:
                for row in rows:
                    iotId = row["iot_id"]
                    openId = row["open_id"]
                    sn = row["sn"]
                    productModel = row["product_serial_no"]
                    print(
                        f"账号：{phone},环境：{self.env},用户id:{userId} 设备ID:{iotId}，用户ID:{openId} 购买运存 和事件")
                    print(f"产品型号：{productModel} sn:{sn}")
                    self.buy(iotId, openId)
        else:
            print("用户不存在")

    # 通过账号 购买运存
    def buyBuySN(self, SN):
        database = "ugreen_dpt_" + self.env
        sqlx = f"select iot_id,open_id,sn,product_serial_no,user_id from ipc_bind_record where status = 1 and bind_type = 0 and  sn = '{SN}'"
        db = ipc_db.DB(self.env, database)
        bindIfo = db.select(sqlx)
        if bindIfo:
            iotId = bindIfo[0]["iot_id"]
            openId = bindIfo[0]["open_id"]
            userId = bindIfo[0]["user_id"]
            sn = bindIfo[0]["sn"]
            productModel = bindIfo[0]["product_serial_no"]
            print(f"账号：{SN},环境：{self.env},userId:{userId} iotId:{iotId}，openId:{openId} 购买运存 和事件")
            print(f"产品型号：{productModel} sn:{sn}")
            self.buy(iotId, openId)

    # 账号绑定情况
    def bindInfo(self, phone):
        phonex = AESUtil.encrypt(key, phone)
        sql = f"select user_id from user where status = 1 and user_mobile = '{phonex}' and destroy_status = 1"
        if self.env == "ces":
            sql = f"select user_id from user where status = 1 and user_mail = '{phonex}' and destroy_status = 1"
        database = "ugreen_dpt_user_" + self.env
        db = ipc_db.DB(self.env, database)
        data = db.select(sql)
        if data and len(data) > 0:
            userId = data[0]["user_id"]
            database = "ugreen_dpt_" + self.env
            sqlx = f"select iot_id,open_id,sn,product_serial_no from ipc_bind_record where status = 1 and bind_type = 0 and  user_id = '{userId}'"
            db = ipc_db.DB(self.env, database)
            rows = db.select(sqlx)
            if rows and len(rows) > 0:
                for row in rows:
                    iotId = row["iot_id"]
                    self.getIotBuy(iotId)
                    openId = row["open_id"]
                    sn = row["sn"]
                    productModel = row["product_serial_no"]
                    print(
                        f"产品型号：{productModel} sn:{sn} 账号：{phone},环境：{self.env},用户id:{userId} 设备ID:{iotId}，用户ID:{openId} ")
            else:
                print(f"账号：{phone} userId:{userId} 没有任何绑定设备")
        else:
            print("用户不存在")

    # 账号下全部绑定情况
    def allBindInfo(self, phone):
        phonex = AESUtil.encrypt(key, phone)
        sql = f"select user_id from user where status = 1 and user_mobile = '{phonex}' and destroy_status = 1"
        if self.env == "ces":
            sql = f"select user_id from user where status = 1 and user_mail = '{phonex}' and destroy_status = 1"
        database = "ugreen_dpt_user_" + self.env
        db = ipc_db.DB(self.env, database)
        data = db.select(sql)
        if data and len(data) > 0:
            userId = data[0]["user_id"]
            database = "ugreen_dpt_" + self.env
            sqlx = f'''
                            SELECT iot_id, open_id, sn, product_serial_no, bind_time, unbind_time,status
                FROM (
                    SELECT 
                        iot_id, open_id, sn, product_serial_no, bind_time, unbind_time,status,
                        ROW_NUMBER() OVER (PARTITION BY iot_id ORDER BY bind_time DESC) AS rn
                    FROM ipc_bind_record
                    WHERE user_id = '{userId}'
                ) t
                WHERE rn = 1 order by status asc ;
            '''
            db = ipc_db.DB(self.env, database)
            rows = db.select(sqlx)
            if rows and len(rows) > 0:
                for row in rows:
                    iotId = row["iot_id"]
                    self.getIotBuy(iotId)
                    openId = row["open_id"]
                    sn = row["sn"]
                    productModel = row["product_serial_no"]
                    status = "绑定"
                    bindTime = int(row["bind_time"] / 1000)
                    bindTime = datetime.datetime.fromtimestamp(bindTime).strftime('%Y-%m-%d %H:%M:%S')
                    unbindTime = int(row["unbind_time"] / 1000)
                    if row["status"] == 0:
                        status = "解绑"
                        unbindTime = datetime.datetime.fromtimestamp(unbindTime).strftime('%Y-%m-%d %H:%M:%S')
                    print(
                        f"产品型号：{productModel} sn:{sn} 账号：{phone},环境：{self.env},用户id:{userId} 设备ID:{iotId}，用户ID:{openId} 绑定状态是:{status} 绑定时间是：{bindTime} 解绑时间是：{unbindTime}")
            else:
                print(f"账号：{phone} userId:{userId} 没有任何绑定设备")
        else:
            print("用户不存在")

    # sn 绑定情况
    def getSnInfo(self, sn):
        # 上报记录，以及状态，三元组
        database = "ugreen_dpt_metadata_" + self.env
        sql = f"SELECT sn.sn,sn.product_model,meta.product_key,meta.device_name,sn.status from ugreen_sn as sn LEFT JOIN ugreen_sn_meta meta on sn.sn = meta.sn WHERE sn.sn = '{sn}'"
        db = ipc_db.DB(self.env, database)
        meta = db.select(sql)
        if meta:
            meta = meta[0]
            product_model = meta["product_model"]
            print(
                f"基本信息：sn:{sn} 状态：{meta['status']} productModel：{meta['product_model']},productKey:{meta['product_key']} DeviceName:{meta['device_name']}")
            database = "ugreen_dpt_" + self.env
            sql = f"SELECT user_id,open_id,iot_id,status,bind_type from ipc_bind_record WHERE sn = '{sn}' and status = 1 "
            db = ipc_db.DB(self.env, database)
            bindInfo = db.select(sql)
            if bindInfo:
                for user in bindInfo:
                    userId = user["user_id"]
                    bind_status = "解绑"
                    if user["status"] == 1:
                        bind_status = "绑定状态"
                    bindType = "拥有者"
                    if user["bind_type"] == 1:
                        bindType = "被分享"
                    self.getIotBuy(user["iot_id"])
                    print(f"绑定信息：用户Id:{userId} openId:{user['open_id']} iotId:{user['iot_id']}  绑定状态是：{bind_status} 绑定类型是：{bindType}")
                    database = "ugreen_dpt_user_" + self.env
                    sql = f"SELECT user_mobile,user_mail from user WHERE user_id = '{userId}' "
                    db = ipc_db.DB(self.env, database)
                    userInfo = db.select(sql)
                    if userInfo:
                        userx = userInfo[0]
                        if self.env == "ces":
                            userMobile = userx["user_mail"]
                            phonex = AESUtil.decrypt(key, userMobile)
                            print(f"用户的邮箱是：{phonex}")
                        else:
                            userMobile = userx["user_mobile"]
                            phonex = AESUtil.decrypt(key, userMobile)
                            print(f"用户的手机号是：{phonex}")

    # 强制解绑
    def forceUnBind(self, sn):
        database = f"ugreen_dpt_{self.env}"
        sql = f"select open_id,iot_id from ipc_bind_record where sn = '{sn}' and `status` = 1 and bind_type = 0"
        db = ipc_db.DB(self.env, database)
        userInfo = db.select(sql)
        if userInfo:
            d = userInfo[0]
            openId = d["open_id"]
            iotId = d["iot_id"]
            self.unbind(iotId, openId)
            sqls = [
                f"delete from user_bind_info where device_unique_code = '{sn}';",
                f"delete from ipc_bind_record where sn = '{sn}';",
                f"delete from ipc_share_qr_code where device_unique_code = '{sn}';",
                f"delete from ipc_share_record where device_unique_code = '{sn}';",
                f"delete from ipc_contact_label where device_unique_code = '{sn}';",
                f"delete from ipc_device_event_record where sn = '{sn}';",
            ]
            for sql in sqls:
                print(sql)
                db = ipc_db.DB(self.env, database)
                db.insert(sql)
        else:
            print("不存在绑定")

    def checkMeta(self):
        for model in models.keys():
            database = f"ugreen_dpt_metadata_{self.env}"
            total = f"select count(1) as num from ugreen_meta where  product_model = '{model}'"
            unUse = f"select count(1) as num from ugreen_meta where `status` = 0 and product_model = '{model}'"
            db = ipc_db.DB(self.env, database)
            total = db.select(total)
            unUse = db.select(unUse)
            sql = f"select count(1) as num from user_bind_info where product_serial_no = '{model}'"
            database = f"ugreen_dpt_{self.env}"
            db = ipc_db.DB(self.env, database)
            data = db.select(sql)
            print(
                f"环境：{self.env} 产品型号：{model} 名称是：{models[model]} 绑定人数：{data[0]['num']}三元组总量是：{total[0]['num']} 未使用：{unUse[0]['num']} ")


if __name__ == '__main__':

    rtcx = Rtcx("ces")

    sn = "b922fb9756a05a98"

    # 强制解绑某个设备
    # rtcx.forceUnBind(sn)
