#! /usr/bin/env python3
# coding: utf-8
import re
from nornir.plugins.tasks.networking import netmiko_send_command, netmiko_send_config, netmiko_file_transfer

#exracting libraries
from nor_support import extractsState, extractsLoopback, extractsQos, extractsRouteStatic, extractsA_Sdslwan, extractsFibrewan, extractsLSwan

###################
# Read only tasks #
###################


############## functions that ecxecute all commands ###############

def sh_vrrp_brief(task): 
	task.run(
		task=netmiko_send_command,
		command_string="sh vrrp brief",
	)
	host = str(task.results[0].host)
	output = extractsState(task.results[0].result, host)
	filename=host+ ".txt"
	host_file= open('tmp/'+filename, 'w')
	host_file.write(output)
	host_file.write("\n")
	host_file.close()
	#print("sh vrrp brief executed ! \n")


def sh_int_loopback(task):
	task.run(
		task=netmiko_send_command,
		command_string="sh inte loo0",
	)
	host = str(task.results[0].host)
	output = extractsLoopback(task.results[0].result, host)
	filename=host+ ".txt"
	host_file= open('tmp/'+filename, 'a')
	host_file.write(output)
	host_file.write("\n")
	host_file.close()
	#print("sh int loopback executed ! \n")


def sh_policy_map(task):
	task.run(
		task=netmiko_send_command,
		command_string="sh policy-map | inc QOS",
	)
	host = str(task.results[0].host)
	output = extractsQos(task.results[0].result, host)
	filename=host+ ".txt"
	host_file= open('tmp/'+filename, 'a')
	host_file.write(output)
	host_file.write("\n")
	host_file.close()
	#print("sh policy-map executed ! \n")


def sh_ip_route_static(task):
	task.run(
		task=netmiko_send_command,
		command_string="sh ip route static",
	)
	host = str(task.results[0].host)
	output = extractsRouteStatic(task.results[0].result, host)
	filename=host+ ".txt"
	host_file= open('tmp/'+filename, 'a')
	host_file.write(output)
	host_file.write("\n")
	host_file.close()
	#print("sh ip route static executed ! \n")



def sh_ip_wan(task):
	task.run(
		task=netmiko_send_command,
		command_string="sh ip interface brief | include [D,d]ialer[1-9]",
	)
	host = str(task.results[0].host)
	output = extractsA_Sdslwan(task.results[0].result, host)

	if output == "false" :
		task.run(
			task=netmiko_send_command,
			command_string="sh ip interface brief | include GigabitEthernet9\.",
		)
		output = extractsFibrewan(task.results[1].result, host)

	if output == "false" :
		task.run(
			task=netmiko_send_command,
			command_string="sh ip interface brief | inc Serial",
		)
		output = extractsLSwan(task.results[2].result, host)

	filename=host+ ".txt"
	host_file= open('tmp/'+filename, 'a')
	host_file.write(output)
	host_file.write("\n")
	host_file.close()
	#print("sh ip wan executed ! \n")



######################################################## Other Tasks might be usefull ###############################################

def sh_stack_info(task, start_time):
	"""
	Task collecting stack info, regarding number of members
	version, next boot info, flash content and available space,
	outputProcessed = {
		'version': 'VXXXXXX' (str),
		'stackSize': X (int),
		'FlashY': XXXXX (str),
		...
	}
	"""
	outputRaw = {}
	outputProcessed = {}
	play_index = 0
	task.run(
		task=netmiko_send_command,
		command_string="show version",
	)
	outputRaw[play_index] = task.results[play_index].result
	outputProcessed['version'] = extractsVersion(outputRaw[play_index])
	print(f"Got VERSION at: {time.time() - start_time} seconds")

	play_index += 1
	task.run(
		task=netmiko_send_command,
		command_string="show switch",
	)
	outputRaw[play_index] = task.results[play_index].result
	outputProcessed['stackSize'] = extractsStackSize(outputRaw[play_index])
	print(f"Got STACKSIZE at: {time.time() - start_time} seconds")

	for stack in range(1, outputProcessed['stackSize'] + 1):
		play_index += 1
		task.run(
			task=netmiko_send_command,
			command_string="dir flash{}:".format(stack),
		)
		outputRaw[play_index] = task.results[play_index].result
		outputProcessed['Flash{}'.format(stack)] = extractsFlashFreeSpace(outputRaw[play_index])
		outputProcessed['Binaries'] = extractsFlashContent(outputRaw[play_index])
		print(f"Got FREE MEMORY and binary folders or files at: {time.time() - start_time} seconds")