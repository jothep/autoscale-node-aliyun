# -*- coding: utf-8 -*-

# if the python sdk is not install using 'sudo pip install aliyun-python-sdk-ecs'
# if the python sdk is install using 'sudo pip install --upgrade aliyun-python-sdk-ecs'
# make sure the sdk version is 2.1.2, you can use command 'pip show aliyun-python-sdk-ecs' to check

import json
import logging
import time

from aliyunsdkecs.request.v20140526.CreateInstanceRequest import CreateInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest
from aliyunsdkecs.request.v20140526.StopInstanceRequest import StopInstanceRequest
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest

import auth

# 删除 ECS 需要指定 ip
ip = "10.0.14.43"

# configuration the log output formatter, if you want to save the output to file,
# append ",filename='ecs_invoke.log'" after datefmt.

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

clt = auth.auth()


def create_instance_action():
    instance_id = create_after_pay_instance(image_id=IMAGE_ID, instance_type=INSTANCE_TYPE,
                                            security_group_id=SECURITY_GROUP_ID, vswitch_id=VSWITCH_ID)
    check_instance_running(instance_id=instance_id)
    ip = get_instance_ip_by_id(instance_id=instance_id)
    return ip


def create_prepay_instance_action():
    instance_id = create_prepay_instance(image_id=IMAGE_ID, instance_type=INSTANCE_TYPE,
                                         security_group_id=SECURITY_GROUP_ID, vswitch_id=VSWITCH_ID)
    check_instance_running(instance_id=instance_id)


# create one after pay ecs instance.
def create_after_pay_instance(image_id, instance_type, security_group_id, vswitch_id):
    request = CreateInstanceRequest();
    request.set_ImageId(image_id)
    request.set_SecurityGroupId(security_group_id)
    request.set_InstanceType(instance_type)
    request.set_VSwitchId(vswitch_id)
    request.set_SystemDiskSize("100")
    request.set_InstanceName(instance_name)
    request.set_KeyPairName("saltstack1")
    request.set_InstanceChargeType("PostPaid")
    response = _send_request(request)
    instance_id = response.get('InstanceId')
    logging.info("instance %s created task submit successfully.", instance_id)
    return instance_id;


# create one prepay ecs instance.
def create_prepay_instance(image_id, instance_type, security_group_id, vswitch_id):
    request = CreateInstanceRequest();
    request.set_ImageId(image_id)
    request.set_SecurityGroupId(security_group_id)
    request.set_InstanceType(instance_type)
    request.set_VSwitchId(vswitch_id)
    request.set_Period(1)
    request.set_InstanceChargeType('PrePaid')
    request.set_InstanceName(instance_name)
    request.set_KeyPairName("saltstack1")
    response = _send_request(request)
    instance_id = response.get('InstanceId')
    logging.info("instance %s created task submit successfully.", instance_id)
    return instance_id;


def delete_after_pay_instance(ip):
    instance_id = get_instance_id_by_ip(ip)
    check_instance_stopped(instance_id)
    request = DeleteInstanceRequest()
    request.set_InstanceId(instance_id)
    _send_request(request)
    logging.info("instance %s delete task submit successfully.", instance_id)


def check_instance_running(instance_id):
    detail = get_instance_detail_by_id(instance_id=instance_id, status=INSTANCE_RUNNING)
    index = 0
    while detail is None and index < 60:
        detail = get_instance_detail_by_id(instance_id=instance_id);
        time.sleep(10)

    if detail and detail.get('Status') == 'Stopped':
        logging.info("instance %s is stopped now.")
        start_instance(instance_id=instance_id)
        logging.info("start instance %s job submit.")

    detail = get_instance_detail_by_id(instance_id=instance_id, status=INSTANCE_RUNNING)
    while detail is None and index < 60:
        detail = get_instance_detail_by_id(instance_id=instance_id, status=INSTANCE_RUNNING);
        time.sleep(10)

    logging.info("instance %s is running now.", instance_id)
    return instance_id;


def check_instance_stopped(instance_id):
    detail = get_instance_detail_by_id(instance_id=instance_id, status=INSTANCE_STOPPED)
    index = 0
    while detail is None and index < 60:
        detail = get_instance_detail_by_id(instance_id=instance_id, status="Running");
        time.sleep(10)

    if detail and detail.get('Status') == 'Running':
        logging.info("instance %s is running now.")
        stop_instance(instance_id=instance_id)
        logging.info("stop instance %s job submit.")

    detail = get_instance_detail_by_id(instance_id=instance_id, status=INSTANCE_STOPPED)
    while detail is None and index < 60:
        detail = get_instance_detail_by_id(instance_id=instance_id, status=INSTANCE_STOPPED);
        time.sleep(10)

    logging.info("instance %s is stopped now.", instance_id)
    return instance_id;


def start_instance(instance_id):
    request = StartInstanceRequest()
    request.set_InstanceId(instance_id)
    _send_request(request)


def stop_instance(instance_id):
    request = StopInstanceRequest()
    request.set_InstanceId(instance_id)
    _send_request(request)


# output the instance owned in current region.
def get_instance_detail_by_id(instance_id, status='Stopped'):
    logging.info("Check instance %s status is %s", instance_id, status)
    request = DescribeInstancesRequest()
    request.set_InstanceIds(json.dumps([instance_id]))
    response = _send_request(request)
    instance_detail = None
    if response is not None:
        instance_list = response.get('Instances').get('Instance')
        for item in instance_list:
            if item.get('Status') == status:
                instance_detail = item
                break;
        return instance_detail;


def get_instance_id_by_ip(ip):
    logging.info("Check ip %s", ip)
    request = DescribeInstancesRequest()
    request.set_PageSize(100)
    ipaddr = json.dumps([ip])
    request.set_PrivateIpAddresses(ipaddr)
    response = _send_request(request)
    instance_id = response.get("Instances").get("Instance")[0].get("InstanceId")
    return instance_id


def get_instance_ip_by_id(instance_id):
    logging.info("Check instance_id %s", instance_id)
    request = DescribeInstancesRequest()
    request.set_PageSize(100)
    id = json.dumps([instance_id])
    request.set_InstanceIds(id)
    response = _send_request(request)
    ip = response.get("Instances").get("Instance")[0].get("VpcAttributes").get("PrivateIpAddress").get("IpAddress")[0]
    return ip


# send open api request
def _send_request(request):
    request.set_accept_format('json')
    try:
        response_str = clt.do_action_with_exception(request)
        logging.info(response_str)
        response_detail = json.loads(response_str)
        return response_detail
    except Exception as e:
        logging.error(e)


# 标准配置项，一般无需修改
IMAGE_ID = 'm-wz9f00n0jaawe30inaki'
SECURITY_GROUP_ID = 'sg-wz9cwc8a1y7sjf2aytb7'
VSWITCH_ID = "vsw-wz9hj3kokqpxkwnfylp3r"
INSTANCE_RUNNING = 'Running'
INSTANCE_STOPPED = 'Stopped'

# 创建 ECS 需要修改实例名称，指定实例类型
instance_name = "OpenAPItest"
# INSTANCE_TYPE = 'ecs.s2.large'  # 2c4g generation 1
INSTANCE_TYPE = 'ecs.sn2.large'  # 4c16g
#INSTANCE_TYPE = 'ecs.n1.tiny'  # 1c1g
#INSTANCE_TYPE = 'ecs.d1.2xlarge' # 8c32g

# 删除 ECS 需要指定 ip
#ip = "10.0.14.9"

if __name__ == '__main__':
    logging.info("Create ECS by OpenApi!")
    #create_instance_action()
    delete_after_pay_instance(ip=ip)
    # create_prepay_instance_action()

