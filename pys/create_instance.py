# -*- coding: utf-8 -*-

from aliyunsdkecs.request.v20140526 import CreateInstanceRequest

import auth

# 自定义镜像
image_id = "m-wz9f00n0jaawe30inaki"

# 实例类型
## 1核1GB
instance_type = "ecs.n1.tiny"
## 4核16GB
# instance_type = "ecs.sn2.large"

# kube-node
security_group_id = "sg-wz9cwc8a1y7sjf2aytb7"

# kube-net
vswitch_id = "vsw-wz9hj3kokqpxkwnfylp3r"

# 付费类型
## 包年包月
# instance_charge_type = "PrePaid"
## 按量付费
instance_charge_type = "PostPaid"

instance_name = "PythonTestApi"
key_pair_name = "saltstack1"

def main():
    # 创建 request，并设置参数
    request = CreateInstanceRequest.CreateInstanceRequest()
    request.set_ImageId(image_id)
    request.set_InstanceType(instance_type)
    request.set_SecurityGroupId(security_group_id)
    request.set_VSwitchId(vswitch_id)
    request.set_InstanceName(instance_name)
    request.set_KeyPairName(key_pair_name)
    request.set_InstanceChargeType(instance_charge_type)

    # 获取授权信息
    client = auth.auth()

    # 发起 API 请求并打印返回
    response = client.do_action_with_exception(request)
    ret = response.decode('utf-8')
    print(ret)


if __name__ == "__main__":
    main()

