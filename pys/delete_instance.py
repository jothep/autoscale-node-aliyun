#!/usr/bin/env python3
# -*- coding: utf8 -*-

from aliyunsdkecs.request.v20140526 import DeleteInstanceRequest

import auth

instance_id = "i-wz94aqde7fblxuko00qx"

# 创建 request，并设置参数
request = DeleteInstanceRequest.DeleteInstanceRequest()
request.set_InstanceId(instance_id)

# 获取授权信息
client = auth.auth()

# 发起 API 请求并打印返回
response = client.do_action_with_exception(request)
ret = response.decode('utf-8')
print(ret)

