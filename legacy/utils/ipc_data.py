from ipc_db import DB

if __name__ == '__main__':

    bind_sql = "select product_serial_no,device_unique_code from user_bind_info WHERE product_serial_no in ('Camera001','010001') order by product_serial_no;"
    database = "ugreen_dpt_test"
    db = DB("test", database)
    bindInfos = db.select(bind_sql)
    for row in bindInfos:
        sn = row["device_unique_code"]
        product_model = row["product_serial_no"]
        print(product_model + "@@" + sn)

        # 查询全部 SN
        sn_sql = f"SELECT sn,product_model,region,mac,first_time,`status`,product_no,sku,scan_in_time from ugreen_sn where sn = '{sn}' and product_model = '{product_model}'"
        database = "ugreen_dpt_metadata_test"
        db = DB("test", database)
        snData = db.select(sn_sql)

        for rowx in snData:
            # 查询全部 密钥
            select_sql = f"SELECT sn,product_model,version,public_key from ugreen_sn_secret where sn='{sn}' and product_model='{product_model}'"
            rows = db.select(select_sql)
            if rows and len(rows) > 0:
                for r in rows:
                    version = r["version"]
                    print(product_model + "_" + sn+"_"+version)

