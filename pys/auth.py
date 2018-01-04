# -*- coding: utf-8 -*-

# modify key_id and key_secret then
# mv auth_default.py auth.py

from aliyunsdkcore.client import AcsClient

def auth():
    # 基础授权信息
#    access_key_id = "access_key_id"
#    access_key_secret = "access_key_secret"
#    region_id = "cn-shenzhen"
    access_key_id = " "
    access_key_secret = " "
    region_id = "cn-shenzhen"

    # 创建 AcsClient 实例
    client = AcsClient(
        access_key_id,
        access_key_secret,
        region_id
    )
    return client

