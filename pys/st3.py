#!/usr/bin/env python
#encoding:utf8

import json
import os
import requests
import re
import socket

#get nodes list from heapster
def get_nodes(srv):
    url = 'http://' + srv + '/api/v1/model/nodes'
    content = requests.get(url).content
    ls = eval(content)
    return ls

#get value from dict type of heapster
def get_val(dict_1):
    if isinstance(dict_1, dict):
        tmpvalue = dict_1["metrics"][-1]
        return int(tmpvalue['value'])

#get full working set dict
def get_ful_ws_dic(srv, nodes):
	dict_ws = {}
	for nd in nodes:
		url = 'http://' + srv + '/api/v1/model/nodes/' + nd + '/metrics/memory/working_set'
		content = requests.get(url).content
		dic = eval(content)
		val = get_val(dic)
		dict_ws.setdefault(nd, val)
	return dict_ws

#get full usage dict
def get_ful_use_dic(srv, nodes):
	dict_use = {}
	for nd in nodes:
		url = 'http://' + srv + '/api/v1/model/nodes/' + nd + '/metrics/memory/usage'
		content = requests.get(url).content
		dic = eval(content)
		val = get_val(dic)
		dict_use.setdefault(nd, val)
	return dict_use

#reverse from node dict min->max, make list
def rev_node(dic):
	dic_to_ls = sorted(dic.iteritems(),key=lambda t:t[1],reverse=False)
	return dic_to_ls

#get lowest cost node
def lowest_name(dic_lis):
	return dic_lis[0][0]

#get lowest cost node ip
def lowest_ip(dic_lis):
	name = lowest_name(dic_lis)
	get_str = "".join(re.findall(r"^aliyun-[0-9a-z\_]{3,4}-node-(.*)", name))
	str_ip = get_str.replace('-', '.')
	return str_ip


#cluster mem used, total is memory/node_capacity
def mem_used(srv, nodes):
    sum = 0
    for node in nodes:
        url = 'http://' + srv + '/api/v1/model/nodes/' + node + '/metrics/memory/usage'
        content = requests.get(url).content
        dic = eval(content)
        sum += get_val(dic)
    return sum

#cluster mem working_set, total is memory/node_allocatable
def mem_hot(srv, nodes):
    sum = 0
    for node in nodes:
        url = 'http://' + srv + '/api/v1/model/nodes/' + node + '/metrics/memory/working_set'
        content = requests.get(url).content
        dic = eval(content)
	#print dic
        sum += get_val(dic)
    return sum

single_capacity = 15085289472	#one node's allocatable mem capacity
#cluster allocate capacity
def fullmem(single_capacity, nodes):
    count = len(nodes)
    full = count * single_capacity
    return full

#calculate differenct of hot and full
def diff_mem(full, hot):
    free_mem = full - hot
    return free_mem
	
def resource_more_or_less(ip, single_capacity):
    nodes = get_nodes(ip)
    hot = mem_hot(ip, nodes)
    full = fullmem(single_capacity, nodes)
    diff = diff_mem(full, hot)
    diffM = diff/1024/1024
    if diff < 3 * single_capacity :
        print ('resources had %dMi ,scarce.') % diffM
        return 'scarce'
    elif diff > 5 * single_capacity :
        print ('resources had %dMi , idle.') % diffM
        return 'idle'
    else :
        print ('resources had %dMi , balance.') % diffM
        return 'balance'
	
#calculate percent of mem_used
def use_per(nodes, usedmem):
    count = len(nodes)
    #total memory is memory/node_capacity
    fullmem = float(count * 16658153472) 
    pr = float(usedmem/fullmem)
    useper = format(pr, '0.2%')
    print "used percent is:",
    print useper
    return useper

#calculate percent of mem_hot
def hot_per(nodes, hotmem):
    count = len(nodes)
    #total memory is memory/node_allocatable
    fullmem = float(count * 15085289472)
    hotper = format(hotmem/fullmem, '0.2%')
    print "hot percent is:",
    print hotper
    return hotper

#calculate resource used rate
def calc_percents(ip):
    nodes = get_nodes(ip)
    used = mem_used(ip, nodes)
    hot = mem_hot(ip, nodes)
    up = use_per(nodes, used)
    hp = hot_per(nodes, hot)
    return up, hp

if __name__ == "__main__":
#replace ip to domain name in pod
    ip = socket.gethostbyname('heapster.kube-system')
    #ip = '10.0.14.249:30082'
    e = calc_percents(ip)
    #print e[0]
    #print e[1]
    resource_more_or_less(ip, single_capacity)
