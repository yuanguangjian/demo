import uuid
import rtcxUtil
import mysqlUtil as mysql
from ipc项目.AESUtil import AESUtil

baseData = {
    "id": str(uuid.uuid4()),
    "params": {},
    "request": {
        "apiVer": "1.0.0"
    },
    "version": "1.0"
}
product = ["event_1_year", "continuous_1_year"]
envs = ["dev", "test", "dvt"]
key = "gh&*$P3124334343"


class Rtcx:
    def __init__(self):
        print("初始化")

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
            result = rtcxUtil.request(path, baseData)
            print(f"购买：{specification}，结果是：{result}")

    def buyxx(self, env, phone):
        phonex = AESUtil.encrypt(key, phone)
        u = "ugreen_dpt_user_" + env
        sql = f"select user_id from user where status = 1 and user_mobile = '{phonex}'"
        data = mysql.getData(env, u, sql)
        if data:
            for user in data:
                userId = user["user_id"]
                d = "ugreen_dpt_" + env
                sqlx = f"select iot_id,open_id,sn,product_serial_no from ipc_bind_record where status = 1 and bind_type = 0 and  user_id = '{userId}'"
                bindIfo = mysql.getData(env, d, sqlx)
                if bindIfo:
                    for iot in bindIfo:
                        iotId = iot["iot_id"]
                        openId = iot["open_id"]
                        sn = iot["sn"]
                        productModel = iot["product_serial_no"]
                        print(
                            f"手机号：{phone},环境：{env},用户id:{userId} 设备ID:{iotId}，用户ID:{openId} 购买运存 和事件")
                        print(f"产品型号：{productModel} sn:{sn}")
                        self.buy(iotId, openId)
        else:
            print("用户不存在")

def unbind(self, env, sn):
    database = f"ugreen_dpt_{env}"
    sql = f"select open_id,iot_id from ipc_bind_record where sn = '{sn}'"
    data = mysql.getData(env, database, sql)
    if data:
        for d in data:
            openId = d["open_id"]
            iotId = d["iot_id"]

    sqls = [
        "delete from user_bind_info where sn = '%s'",
        "delete from ipc_bind_record where sn = '%s'"
        "delete from ipc_share_qr_code where device_unique_code = '%s'"
        "delete from ipc_share_record where device_unique_code = '%s'"
    ]
    for sql in sqls:
        sql = sql.format(sn)
        print(sql)
        mysql.delete(env, database, sql)

    # 查询sn信息：


def getSnInfo(self, sn, env):
    # 上报记录，以及状态，三元组
    database = "ugreen_dpt_metadata_" + env
    sql = f"SELECT sn.sn,sn.product_model,meta.product_key,meta.device_name,sn.status from ugreen_sn as sn LEFT JOIN ugreen_sn_meta meta on sn.sn = meta.sn WHERE sn.sn = '{sn}'"
    metaInfo = mysql.getData(env, database, sql)
    if metaInfo:
        for meta in metaInfo:
            print(
                f"基本信息：sn:{sn} 状态：{meta['status']} 产品型号：{meta['product_model']},产品key:{meta['product_key']} 设备名称{meta['device_name']}")
            database = "ugreen_dpt_" + env
            sql = f"SELECT user_id,open_id,iot_id from ipc_bind_record WHERE sn = '{sn}' and `status` = 1 and bind_type = 0 "
            bindInfo = mysql.getData(env, database, sql)
            if bindInfo:
                for user in bindInfo:
                    userId = user["user_id"]
                    print(f"绑定信息：用户Id:{userId} openId:{user['open_id']} iotId:{user['iot_id']}")
                    database = "ugreen_dpt_user_" + env
                    sql = f"SELECT user_mobile,user_mail from user WHERE user_id = '{userId}' "
                    user_Info = mysql.getData(env, database, sql)
                    if user_Info:
                        for userx in user_Info:
                            userMobile = userx["user_mobile"]
                            phonex = AESUtil.decrypt(key, userMobile)
                            print(f"用户的手机号是：{phonex}")


if __name__ == '__main__':

    # 购买
    phone = "13662558350"
    rtcx = Rtcx()
    rtcx.buyxx("dvt", phone)

    # for env in envs:
    #     rtcx.buyxx(env, phone)
    #     print("\n")
    #     print("\n")

    # 查询 sn 信息
    sn = "I50000U59M100014"
    # rtcx.getSnInfo(sn,"test")
