import multiprocessing
import time

def read_data():
	random_num = []
	filename = r"C:\Users\hp1\Desktop\OS\random_num.txt"
	f = open(filename,"r")
	while(True):
		num = f.readline()
		if(num):
			random_num.append(int(num.strip()))
		else:
			break
	f.close()
	return random_num
	# read data file

def write_data(l):
	filename = r"C:\Users\hp1\Desktop\OS\sorted_num.txt"
	f = open(filename,"w")
	for item in l:
		f.write(str(item))
		f.write('\n')
	f.close()
	# write sorted data

def data_split(source):
	length = len(source)
	mid = int(length/2)
	front = source[0:mid]
	back = source[mid:length]
	del source[:]	# may not be efficient 
	return front,back

def quickSort(L, low, high):
    i = low 
    j = high
    if i >= j:
        return L
    key = L[i]
    while i < j:
        while i < j and L[j] >= key:
            j = j-1                                                             
        L[i] = L[j]
        while i < j and L[i] <= key:    
            i = i+1 
        L[j] = L[i]
    L[i] = key 
    quickSort(L, low, i-1)
    quickSort(L, j+1, high)
    return L
    # Quick_Sort by iteration
    # used when length of list is less than 50000

def data_merge(front_num,back_num):
	sort = []
	l = front_num+back_num
	length = len(l)
	sort = quickSort(l,0,length-1)
	return sort
	# attention, smaller number comes first

def distribution(l,queue,pipe,process_con):
	length = len(l)
	process_con.acquire()
	if(length < 1000):
		sort = quickSort(l,0,length-1)
		print "length small enough"
		process_con.release()
		# not split any more
	else:
		queue1 = multiprocessing.Queue()
		pipe1 = multiprocessing.Pipe()
		queue2 = multiprocessing.Queue()
		pipe2 = multiprocessing.Pipe()
		# use the queue and pipe
		front,back = data_split(l)
		process_con.release()
		pro1 = multiprocessing.Process(target = distribution,
			args = (front,queue1,pipe1[0],process_con))
		pro2 = multiprocessing.Process(target = distribution,
			args = (back,queue2,pipe2[0],process_con))
		pro1.start()
		pro2.start()
		print pipe1[1].recv()
		print pipe2[1].recv()
		# start the process, and wait for them to terminate
		front_num = queue1.get()
		back_num = queue2.get()
		# get messages from the queue
		del queue1
		del queue2
		# delete the queue
		sort = data_merge(front_num,back_num)
		# merge two rows of data ranked 
	queue.put(sort)
	pipe.send('finished')
		

if __name__ == '__main__':
	t1 = time.time()
	l = read_data()
	t2 = time.time()
	print "Read File Time:",t2-t1
	# read data
	queue = multiprocessing.Queue()
	pipe = multiprocessing.Pipe()
	process_con = multiprocessing.Semaphore(value = 20)
	s = multiprocessing.Process(target = distribution,args = (l,queue,pipe[0],process_con))
	s.start()
	pipe[1].recv()
	sort = queue.get()
	t3 = time.time()
	print "Sort Time:",t3-t2
	# use the queue to send messages
	write_data(sort)
	t4 = time.time()
	print "Write File Time:",t4-t3