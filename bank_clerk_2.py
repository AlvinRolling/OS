import multiprocessing
import time

def read_text():
	f = open("C:\Users\hp1\Desktop\OS\client.txt","r")
	clients = []
	while(True):
		#client_sum = client_sum+1
		line = f.readline()
		if(line):
			element = line.split()
			client_num = element[0]
			client_showup = element[1]
			client_time = element[2]
			clients.append([client_num,client_showup,client_time])
		else:
			break
	return clients
	# read data from the file


def bank_clerk(i,queue,set_info,mutex_call,mutex_client,mutex_print):
	while(True):
		mutex_client.acquire()
		# wait for client
		mutex_call.acquire()
		client_info = queue.get()
		# get the client
		mutex_call.release()
		print "Banker "+str(i)+" is serving client "+str(client_info[0])
		time.sleep(int(client_info.pop(2)))
		finish_time = time.ctime()
		set_info.acquire()
		# down info
		client_info.append(finish_time)
		client_info.append(str(i))
		# append the info 
		set_info.release()
		mutex_print.acquire()
		print_info(client_info)
		# print the info to the file by calling the function
		mutex_print.release()
		print "Client "+str(client_info[0])+" service finished."
		

def get_in_line(order,time_come,service_time,queue,set_info,mutex_client):
	client_info = []
	time.sleep(int(time_come))
	# time to come
	start_time = time.ctime()
	print "Client "+str(order)+" has come."
	set_info.acquire()
	# set the info
	client_info.append(order)
	client_info.append(start_time)
	client_info.append(service_time)
	set_info.release()
	# geting a number 
	print "Client "+str(order)+" is waiting."
	queue.put(client_info)
	# get the client in the queue, waiting for the banker to call
	mutex_client.release()
	# add 1 to the signal client 
	# waiting in line


def print_info(client_info):
	f = open("C:\Users\hp1\Desktop\OS\log.txt","a+")
	print "printing"
	f.write(client_info[0])
	f.write('\t')
	f.write(client_info[1])
	f.write('\t')
	f.write(client_info[2])
	f.write('\t')
	f.write(str(client_info[3]))
	f.write('\n')
	f.close()
	# write info to the file

def _init_():
	n = 3
	# 3 bank clerks in service
	client_queue = read_text() # read data s
	mutex_call = multiprocessing.Semaphore(value = 1)
	set_info = multiprocessing.Semaphore(value = 1)
	mutex_client = multiprocessing.Semaphore(value = 0)
	mutex_print = multiprocessing.Semaphore(value = 1)
	# use the P/V 
	#queue = Queue.Queue()
	queue = multiprocessing.Queue()
	# it's very tricky here, you can't use Queue.Queue()
	# the queue/waiting line
	processes = []
	for i in range(1,n+1):	# this modification let banker starts from 1, not 0.
		t = multiprocessing.Process(target = bank_clerk,args = (i,queue,set_info,mutex_call,mutex_client,mutex_print))
		processes.append(t)
		# the banker processes
	for cli in client_queue:
		t = multiprocessing.Process(target = get_in_line,args = (cli[0],cli[1],cli[2],queue,set_info,mutex_client))
		processes.append(t)
		# the client processes
	return processes


if __name__ == '__main__':
	processes = _init_()
	import pdb
	pdb.set_trace()
	for item in processes:
		pdb.set_trace()
		item.start()
		# start the processes