#!/usr/bin/python
import os, sys, shlex, socket
import subprocess as sp
from settings import masterip, hosts,username
#for x in `cd /etc/init.d ; ls hadoop-hdfs-*` ; do sudo service $x start ; done
services = ['hadoop-hdfs-namenode','hadoop-yarn-resourcemanager','hbase-master','hbase-regionserver']

def call(argstr):
	sp.check_call(shlex.split(argstr))

def clear_data_dirs():
	dfsbase = '/home/{}/data/dfs'.format(username)
	nndir = os.path.join(dfsbase,'nn')
	for f in os.listdir(nndir):
		call('rm -r '+os.path.join(nndir,f))
	dndir = os.path.join(dfsbase,'dn')
	for f in os.listdir(dndir):
		call('rm -r '+os.path.join(dndir,f))	

def clear_log_dirs():
	logbase='/var/log'
	logdirs=os.listdir(logbase)
	for d in logdirs:
		if d.startswith('hadoop') or d.startswith('hbase'):
			logdir = os.path.join(logbase,d)
			for f in os.listdir(logdir):
				p=os.path.join(logdir,f)
				if os.path.isfile(p):
					os.remove(p)

def format_namenode():
	call('sudo -u hdfs hadoop namenode -format')

def stop_services(services):
	for service in reversed(services):
		call("service {} stop".format(service))		

def start_services(services):
	for service in services:
		call("service {} start".format(service))
		if service=='hadoop-hdfs-namenode':
			call('sudo -u hdfs hadoop fs -mkdir /hbase')
			call('sudo -u hdfs hadoop fs -chown hbase:hbase /hbase')


if __name__ == '__main__':
	hostname=socket.gethostname()
	allservices = os.listdir('/etc/init.d')
	services = filter(lambda x: x.startswith("hadoop-hdfs"),allservices)
	services.extend(filter(lambda x: x.startswith('hadoop-yarn'),allservices))
	services.extend(filter(lambda x: x.startswith('zookeeper'),allservices))
	services.extend(sorted(filter(lambda x: x.startswith('hbase'),allservices)))
	print services
	stop_services(services)
	clear_data_dirs()
	clear_log_dirs()
	if hostname == hosts[masterip]:
		format_namenode()
	start_services(services)

