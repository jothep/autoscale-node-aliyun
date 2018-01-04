#!/usr/bin/env python
#encoding:utf8

import sys
sys.path.append('/opt/pys')
import logging
import st3
import manage_ecs
import paramiko
import os
import time
import re
import socket

#get the lowest cost node
def get_low_cos(ip):
	nodes = st3.get_nodes(ip)
	dic = st3.get_ful_ws_dic(ip, nodes)
	list = st3.rev_node(dic)
	name = st3.lowest_name(list)
	ip = st3.lowest_ip(list)
	if len(nodes) >= 3 :
		print('node:%s ip:%s will be removed.' % (name, ip))
	else:
		name = 'None'
	return name

def get_low_cos_ip(ip):
        nodes = st3.get_nodes(ip)
        dic = st3.get_ful_ws_dic(ip, nodes)
        list = st3.rev_node(dic)
        ip = st3.lowest_ip(list)
	if len(nodes) >= 3 :
		return ip
        else:
                ip = 'None'
        return ip

#clean noused in flannel
#def clean_flannel():

#delete lowest cost node
def del_k8s_node(node):
	k8shost = '10.10.10.103'
	k8sport = 12346
	k8suser = 'root'
	key_file = '/opt/id_rsa'  	#k8s-server's key
	key_file_pwd = 'UL9V@RwV_r`V`G=u,<uH' 	#salt-server's key passwd 

	paramiko.util.log_to_file('ssh_key-login.log')		#ssh_key-log 
	privatekey = os.path.expanduser(key_file) 
	try:
    		key = paramiko.RSAKey.from_private_key_file(privatekey)
	except paramiko.PasswordRequiredException:
	    	key = paramiko.RSAKey.from_private_key_file(privatekey,key_file_pwd) #if the key needs pwd

	#start to make ssh connection
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys(filename='/root/.ssh/known_hosts')
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname=k8shost,port=k8sport,username=k8suser,pkey=key)

	#exec salt-ssh init new ecs to k8s cluster
	#stdin,stdout,stderr=ssh.exec_command("kubectl delete no %s" % (node))
	stdin,stdout,stderr=ssh.exec_command("kubectl --kubeconfig /data/salt/file/k8s/1.7/cfg/kubeconfig delete no %s" % (node))
	print stdout.read()
	ssh.close()
	print('Node deleted from k8s cluster.')

def del_node(hpst):
        low_cost_node = get_low_cos(hpst)
        del_k8s_node(low_cost_node)
        strip = get_low_cos_ip(hpst)
	if strip == 'None':
		print 'Not enough node to delete.Keep 2 at least'
	else:
		print 'delete the lowest cost node.'
        	manage_ecs.delete_after_pay_instance(ip=strip)

if __name__ == "__main__":
	hpst = socket.gethostbyname('heapster.kube-system')
	del_node(hpst)
