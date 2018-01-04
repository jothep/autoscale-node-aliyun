#!/usr/bin/env python
#encoding:utf8

import sys
sys.path.append('/opt/pys')
import st3
import crde_slim
import delno
import time
import socket

#hp = '10.0.14.249:30082'
hp = socket.gethostbyname('heapster.kube-system')
var = 1
single_capacity = 15085289472	#one node's allocatable mem capacity
wait_time = 300
wait_time2 = 100

def time_remain(wait_time):
	count = 0
	while (count < wait_time):
		count +=1
		n = wait_time-count
		time.sleep(1)
		sys.stdout.write("Next check after %d seconds. \r" % n,)
		sys.stdout.flush()
		if not n:
			return 'start check'

def change_or_not(hp):
	hot = st3.calc(hp)[1]
	hotnum = float(hot[:-1])
	if hotnum > 24 :
		print 'k8s cluster in heavy pressure.'
		crde_slim.add_k8s_node()		
		return 'added'
	elif 21 < hotnum < 24  :
		print 'k8s cluster in balance.'
		return 'keep'
	else:
		print 'k8s cluster has free resources.'
		delno.del_node(hp)
		return 'deleted'

def monit_by_percents(hp):
	while var == 1 :
		stat = change_or_not(hp)
		if stat == 'keep':
			print 'Keep monitoring...'
			time_remain(wait_time)
		else:
			print 'K8s cluster autoscaled.Please focus on it.'
			time_remain(wait_time)

def change_or_not_num(hp):
	stat = st3.resource_more_or_less(hp, single_capacity)
	if stat == 'scarce' :
		crde_slim.add_k8s_node()
		return 'added'
	elif stat == 'idle' :
                print 'k8s cluster has too many resources.'
                delno.del_node(hp)
		return 'deleted'
	elif stat == 'balance' :
		print 'k8s cluster in balance.'
		return 'keep'
	else:
		return 'error'

def monit_by_num(hp):
	while var == 1 :
		stat = change_or_not_num(hp)
                if stat == 'keep':
                        print 'Keep monitoring...'
                        time_remain(wait_time)
                else:
                        print 'K8s cluster autoscaled.Please focus on it.'
                        time_remain(wait_time2)

	
if __name__ == '__main__':
	#monit_by_percents(hp)
	monit_by_num(hp)	
