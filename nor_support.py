#! /usr/bin/env python3
# coding: utf-8
import re



############## functions that parse output of commands ###############

def extractsState(task_result, host):
	#print(" Connected successfuly to " + host)
	lines = task_result.splitlines()
	if len(lines) == 2 :
		output = re.search(r'\bMASTER|Master|master|Backup|BACKUP|backup\b', lines[1])
		return output[0]
	return "No status"

def extractsLoopback(task_result, host):
	#print(" Connected successfuly to " + host)
	toString = str(task_result)
	output = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", toString)
	return output[0]


def extractsQos(task_result, host):
	#print(" Connected successfuly to " + host)
	lines = task_result.split('\n')
	if len(lines) == 0 :
		return "No QOS found"
	output=lines[0]
	output=str(output)
	output = output.lstrip()
	return output


def extractsRouteStatic(task_result, host):
	#print(" Connected successfuly to " + host)
	lines = task_result.split('\n')
	matching = [ i for i in lines if "Gateway" in i]
	toString=str(matching)
	gateway = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", toString)[0]
	gateway=str(gateway)
	gateway=gateway.lstrip()
	cmdout= "Gateway :"
	cmdout+= gateway
	matching = [ i for i in lines if "via" in i]
	cnt=1
	for item in matching :
		toString = str(item)
		static = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*", toString)[0]
		cmdout+= "|"
		cmdout+= "Route "
		toString=str(cnt)
		cmdout+=toString
		cmdout+= ":"
		cmdout+= static
		cnt=cnt+1
	cmdout= str(cmdout)

	return cmdout



def extractsA_Sdslwan(task_result, host):
	#print(" Connected successfuly to " + host)
	if len(task_result) == 0 :
		#print("not found_ADSL")
		return "false"

	output = task_result.split('\n')
	toString=str(output)
	output = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", toString)[0]
	output = output.lstrip()
	return output


def extractsFibrewan(task_result, host):
	#print(" Connected successfuly to " + host)
	if len(task_result) == 0 :
		#print("not found_FIBRE")
		return "false"

	output = task_result.split('\n')
	toString=str(output)
	output = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", toString)[0]
	output = output.lstrip()
	return output


def extractsLSwan(task_result, host):
	#print(" Connected successfuly to " + host)
	if len(task_result) == 0 :
		#print("not found_LS")
		return "false"

	output = task_result.split('\n')
	toString=str(output)
	output = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", toString)[0]
	output = output.lstrip()
	return output




################################Others Extracts might be usefull ####################################
def extractsIntListFromIntDesc(task_result):
	"""
	Returns list of interfaces alone
	"""
	lines = task_result.split('\n')
	intList = [line.split(' ')[0].lower() for line in lines]
	return intList


def extractsVersion(task_result):
	"""
	Returns IOS version
	"""
	output = []
	firstLine = re.compile('Cisco IOS.*Version.+,')
	version_line = firstLine.findall(task_result)
	version = re.compile('Version [.\w()]+')
	output += version.findall(version_line[0])
	binFile = re.compile('c[0-9]+[\w.-]+\.bin')
	output += binFile.findall(task_result)
	return output


def extractsStackSize(task_result):
	"""
	Returns stack size as integer
	"""
	regex = re.compile('\n[ *][1-8] ?')
	return len(regex.findall(task_result))


def extractsFlashFreeSpace(task_result):
	"""
	Returns free memory from dir flash: command as integer
	"""
	regex = re.compile('[0-9]+\sbytes free?')
	bytes_free = regex.findall(task_result)
	return bytes_free[0].split(' ')[0]


def extractsBootSettings(task_result):
	"""
	Returns dict listing bin file used for next boot and number of
	stack members matching this bin file
	Prints "ERROR" otherwise
	"""
	regex = re.compile('c[0-9]+[\w.-]+\.bin')
	lines = regex.findall(task_result)
	print(lines)
	if len(lines) > 1 and (lines[1:] == lines[:-1]):
		result = {
			'bootfile': lines[0],
			'membersReady': len(lines)
		}
		return result
	elif len(lines) == 1:
		result = {
			'bootfile': lines[0],
			'membersReady': len(lines)
		}
		return result
	else:
		print('ERROR')


def extractsFlashContent(task_result):
	"""
	Returns dict listing bin files or folders containing bin files
	"""
	regex = re.compile('[0-9]+  [-drwx]{4}.*\n')
	lines = regex.findall(task_result)
	#regex for size '[0-9]{3,}(?=  [a-zA-Z]{3} )'
	#regex for tar file 'c[0-9]+[\w.-]+.tar' 
	#regex for bin file 'c[0-9]+[\w.-]+.tar' 
	folder = []
	for line in lines:
		regex2 = re.compile('c[0-9]+[\w.-]+')
		folder += regex2.findall(line)
	return folder