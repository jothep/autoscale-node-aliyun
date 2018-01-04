#!/usr/bin/env python
#encoding:utf8

import sys
sys.path.append('/opt/pys')
import logging
import manage_ecs
import paramiko
import os
import time


#make a salt_roter_file of new ecs on local
def make_salt_roter(ip):
	ips = ip.replace('.', '-')
	nodename = 'aliyun-kube-node-' + ips
	f=open('roster','w')
	f.write(str(nodename)+':'+'\n')
	f.write('    '+'host: '+ip+'\n')
	f.write('    '+'user: root'+'\n')
    	f.write('    '+'port: 12346'+'\n')
    	f.write('    '+'priv: /root/.ssh/id_rsa'+'\n')
	f.close()
	print('Ecs %s\'s roter file maked.' % nodename)
	return nodename

#transport roter of scp
def tran_salt_roter():
        salthost = '10.10.10.103'
        saltport = 12346
        saltuser = 'root'
        key_file = '/opt/id_rsa'         #salt-server's key
        key_file_pwd = 'UL9V@RwV_r`V`G=u,<uH'   #salt-server's key passwd
        localpath = 'roster'                    #salt-roter-file original placed
        remotepath = '/tmp/roster'              #salt-roter-file destination located

        paramiko.util.log_to_file('ssh_key-login.log')          #ssh_key-log
        privatekey = os.path.expanduser(key_file)
        try:
                key = paramiko.RSAKey.from_private_key_file(privatekey)
        except paramiko.PasswordRequiredException:
		key = paramiko.RSAKey.from_private_key_file(privatekey,key_file_pwd) #if the key needs pwd

        #start to make ssh connection
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys(filename='/root/.ssh/known_hosts')
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=salthost,port=saltport,username=saltuser,pkey=key)

        #copy salt roter file to salt-server
        sftp = ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()
	ssh.close()
	print('salt-roter file copied.')

#ssh to salt-server to init k8s node
def salt_makeup_node():
	salthost = '10.10.10.103'
	saltport = 12346
	saltuser = 'root'
	key_file = '/opt/id_rsa'  	#salt-server's key
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
	ssh.connect(hostname=salthost,port=saltport,username=saltuser,pkey=key)

	#exec salt-ssh init new ecs to k8s cluster
	#stdin,stdout,stderr=ssh.exec_command("salt-ssh --roster-file=/tmp/roster -i '*' state.sls sls.k8snodet")
	stdin,stdout,stderr=ssh.exec_command("salt-ssh --roster-file=/tmp/roster -i '*' state.sls sls.system.k8s.init")
	print stdout.read()
	ssh.close()
	print('Node init finished.')

#buy new ecs and add it to k8s cluster
def add_k8s_node():
	newnode = manage_ecs.create_instance_action()
	minname = make_salt_roter(newnode)

	#wait for ecs prepared(just for time, low way...)
	print 'waiting for new ecs ssh preparing...'
	time.sleep(8)
	print 'end of wait'
	
	tran_salt_roter()
	salt_makeup_node()
	print('New node: %s added, job done.' % minname)
	return newnode
	
if __name__ == '__main__':
	add_k8s_node()
