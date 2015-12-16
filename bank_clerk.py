import threading
import time
import Queue



mutex_number = threading.Semaphore(value = 1)
mutex_call = threading.Semaphore(value = 1)
set_info = threading.Semaphore(value = 1)
client = threading.Semaphore(value = 0)
mutex_print = threading.Semaphore(value = 1)
# use the P/V 

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


def bank_clerk(i):
	global client_call
	global client_info
	global client_served
	while(True):
		client.acquire()
		# wait for client
		mutex_call.acquire()
		client_call = client_call+1
		client_to_serve = queue.get()
		# get the client
		mutex_call.release()
		start_time = time.ctime()
		set_info.acquire()
		service_time = int(client_to_serve[0])
		client_info[int(client_to_serve[1])-1].append(start_time)
		set_info.release()
		mutex_print.acquire()
		print "Banker "+str(i)+" is serving client "+str(client_to_serve[1])
		mutex_print.release()
		time.sleep(int(client_to_serve[0]))
		finish_time = time.ctime()
		set_info.acquire()
		# down info
		client_info[int(client_to_serve[1])-1].append(finish_time)
		client_info[int(client_to_serve[1])-1].append(i)
		# append the info 
		client_served = client_served+1
		set_info.release()
		mutex_print.acquire()
		print_info(int(client_to_serve[1])-1)
		# print the info to the file by calling the function
		mutex_print.release()
		mutex_print.acquire()
		print "Client "+str(client_to_serve[1])+" service finished."
		mutex_print.release()
		

def get_in_line(order,time_come,service_time):
	global client_come
	global client_info
	time.sleep(int(time_come))
	# time to come
	start_time = time.ctime()
	set_info.acquire()
	client_info[int(order)-1].append(order)
	client_info[int(order)-1].append(start_time)
	# set the info
	mutex_print.acquire()
	print "Client "+str(order)+" has come."
	mutex_print.release()
	set_info.release()
	mutex_number.acquire()
	# geting a number 
	client_come = client_come+1
	mutex_print.acquire()
	print "Client "+str(order)+" is waiting."
	mutex_print.release()
	mutex_number.release()
	queue.put([service_time,order])
	# get the client in the queue, waiting for the banker to call
	client.release()
	# add 1 to the signal client 
	# waiting in line


def print_info(client_no):
	global client_info
	f = open("C:\Users\hp1\Desktop\OS\log.txt","a+")
	print "printing"
	import pdb
	pdb.set_trace()
	f.write(str(client_info[client_no][0]))
	f.write('\t')
	f.write(client_info[client_no][1])
	f.write('\t')
	f.write(client_info[client_no][2])
	f.write('\t')
	f.write(client_info[client_no][3])
	f.write('\t')
	f.write(str(client_info[client_no][4]))
	f.write('\n')
	f.close()
	# write info to the file

def _init_():
	client_queue = read_text() # read data s
	threads = []
	finished = []
	for i in range(1,n+1):	# this modification let banker starts from 1, not 0.
		t = threading.Thread(target = bank_clerk,args = (i,))
		threads.append(t)
		# the banker threads
	for cli in client_queue:
		t = threading.Thread(target = get_in_line,args = (cli))
		threads.append(t)
		# the client threads
		client_info.append([])
		# allocate enought space for list for further insert
	return threads


if __name__ == '__main__':
	n = 3 
	# 3 bank clerks in service
	global client_come
	global client_call
	global client_served
	global queue
	client_come = 0
	client_call = 0
	client_served = 0
	queue = Queue.Queue()
	# the queue/waiting line
	global client_info
	client_info = []
	threads = _init_()
	for item in threads:
		item.start()
		# start the threads


