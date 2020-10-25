#! /usr/bin/env python3
# coding: utf-8

# Nornir libraries
from nornir.core import InitNornir
from nornir.core.exceptions import NornirExecutionError
from nornir.core.exceptions import CommandError
from nornir.core.exceptions import ConnectionException
from nornir.plugins.tasks.networking import netmiko_file_transfer
from nornir.plugins.functions.text import print_result
from nor_lib import sh_vrrp_brief, sh_int_loopback, sh_policy_map, sh_ip_route_static, sh_ip_wan
from nornir_utilities import nornir_set_creds, std_print


# System libraries
import sys
import io
import os
import time
from datetime import date

# Handling file libraries
import json
import csv
import re
import yaml
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
from pathlib import Path
from shutil import copyfile




print("---->Start script\n")

if len(sys.argv) != 3 : # check if the number of arguments is correct
	print ("You must enter username & password ")
	exit()

print("########################################################")
print("########      Fetching input/output files...   #########")
print("########################################################")



###################### function which allows to update a content in a  file  ###################
def update_file(file_path, pattern, subst):
	#Create temp file
	fh, abs_path = mkstemp()
	with fdopen(fh,'w') as new_file:
		with open(file_path) as old_file:
			for line in old_file:
				new_file.write(line.replace(pattern, subst))
	#Remove original file
	remove(file_path)
	#Move new file
	move(abs_path, file_path) 
#########################################################################



###### initiate output file with header######
with open('input-output/output_files/output.csv', 'w', newline='') as outputfile:
	writer = csv.writer(outputfile)
	writer.writerow(['Nom_site','Code_FR','Master_ID','Ip_lan','Role_routeur','Ip_loopback','Pack_qos','routes_statiques','Ip_wan']) # insert header


####### extract data from inputfile to yaml file to create hosts #############
try:
	with open('input-output/input_files/input.csv', 'r', newline='') as inputfile: #read input file
		inputexists=1
		reader=csv.reader(inputfile)
		next(reader) # skip header
		yaml_host = "---\n"
		for line in reader:
			ip_array = [line[3],line[4]]
			cnt=0
			for ip in range(len(ip_array)):
				if ip_array[ip]: #if array[index] exists
					ip= ip_array[ip]
					ip = ip.replace(" ", "")
					ip.strip()
					if cnt == 1:
						host= "hostSec_"
					else:
						host ="host"
					host+= line[1]
					host = host.replace(" ", "")
					host.strip()
					yaml_host+= host
					yaml_host+=":\n"
					yaml_host+= " "
					yaml_host+= "hostname: "
					yaml_host+= ip
					yaml_host+= "\n"
					yaml_host+= " "
					yaml_host+= "groups:\n"
					yaml_host+= "  "
					yaml_host+= "- cisco_ios\n"
					cnt= cnt+1
					with open('input-output/output_files/output.csv', 'a', newline='') as outputfile: #insert data into output file
						writer = csv.writer(outputfile)
						writer.writerow([line[0],host,line[2],ip])
		
except Exception:
	print("input file not found!")
	print("Please create an input file by this name 'input.csv'")
	exit()



### insert data into hosts yaml file 
host_file= open('hosts.yaml', 'w') 
host_file.write(yaml_host)
host_file.close()
############################end extracting data => yaml file ##################


print("############################################")
print("########         Runing...         #########")
print("############################################")



#############################   Main program  ##################################
nr = InitNornir()# Initialize Nornir object using hosts.yaml and groups.yaml
 
nornir_set_creds(nr, sys.argv[1], sys.argv[2]) # user & password function
run_cmd1 = nr.run(task=sh_vrrp_brief, num_workers=10) # run sh vrrp brief
run_cmd2 = nr.run(task=sh_int_loopback, num_workers=10) # run sh int loopback
run_cmd3 = nr.run(task=sh_policy_map, num_workers=10) # sh policy-map
run_cmd4 = nr.run(task=sh_ip_route_static, num_workers=10) # sh ip route static
run_cmd5 = nr.run(task=sh_ip_wan, num_workers=10) # sh ip wan


copyfile('input-output/output_files/output.csv', 'tmp/copyoutput.csv') # copy of output.csv

with open('tmp/copyoutput.csv', newline='') as tmpfile: #read input file
	reader=csv.reader(tmpfile)
	next(reader) # skip_lan1 header
	for line in reader:
		name_file=line[1]
		name_file+= ".txt"
		for root, dirs, files in os.walk('./tmp'): # itterate over all file existing
			for file in files:
				file= str(file)
				name_file=str(name_file) #get the file name
				if file==name_file:
					with open("tmp/"+name_file, newline='') as tmpfile: #read input file
						reader=csv.reader(tmpfile)
						cmdout=""
						for updateline in reader:
							cmdout+=updateline[0]
							cmdout+=","
						cmdout.strip()
					update=str(line[0])
					update+=","
					update+=str(line[1])
					update+=","
					update+=str(line[2])
					update+=","
					update+=str(line[3])
					pattern=update
					update+=","
					update+=cmdout
					update_file('input-output/output_files/output.csv',pattern, update)
					os.remove("tmp/"+name_file) #remove host file
		

os.remove('tmp/copyoutput.csv') #remove copy


# create a copy of output file for each different day
today = date.today()
filename = "input-output/output_files/"
filename +=str(today)+ "_output.csv"
copyfile('input-output/output_files/output.csv', filename)



# create copy of input file for each different day
today = date.today()
filename = "input-output/input_files/"
filename +=str(today)+ "_intput-done.csv"
copyfile('input-output/input_files/input.csv', filename)
os.remove('input-output/input_files/input.csv') #remove source file

# create log file for connection
today = date.today()
logfile="failed_host_"+ str(today)+ ".log"
with open("log/"+logfile, 'w') as logf: 
	logf.write(" Connection Status         Host           IP address\n") # insert header
	logf.write("-------------------|-----------------|-------------------\n")

########################### End of main program ##############################


#####################  Handle exception   ####################################

object_data=nr.to_dict()# store data object
failed_hosts=str(object_data.get('data').get('failed_hosts'))
list_hosts=failed_hosts.split(",")
inventory=str(object_data.get('inventory'))
inventory=inventory.split("defaults")
list_ip=inventory[0].split("}")

try:
	run_cmd1.raise_on_error()
	run_cmd2.raise_on_error()
	run_cmd3.raise_on_error()
	run_cmd4.raise_on_error()
	run_cmd5.raise_on_error()
except NornirExecutionError:
	print ("----  Error raised ! please find logs in failedhosts file ----: \n" )
	for i in range(len(list_hosts)):
		str_host = list_hosts[i].replace("'", "")
		str_host = str_host.replace("}", "")
		str_host = str_host.replace("{", "")
		str_host = str_host.replace(" ", "")
		str_host.strip()
		for j in range(len(list_ip)) :
			if str_host in list_ip[j] :
				str_ip=re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", list_ip[j])
				str_ip=str(str_ip)
				str_ip = str_ip.replace("['", "")
				str_ip = str_ip.replace("']", "")
				str_ip = str_ip.replace(" ", "")
				str_ip.strip()
				if str_ip == "[]":
					str_ip="ip_syntax_error"
				with open("log/"+logfile, 'a') as logf:
					logf.write("     Failed           "+str_host+"         "+str_ip+"\n") # insert header

###################################################################################


print("                            ---->End of script<----\n")
print("################################## Read me :) ########################################")
print("#####    You can find output in ./input-output/* folder                        ######")
print("#####    If you want to know which host was failed => go to ./log/failedhosts   ######")
print("#####    the tmp folder should be empty!                                         ######")
print("#####    For all other matter, please find the log events in nornir.log file    ######")
print("######################################################################################")
