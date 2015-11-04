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
'''
def data_merge(front_num,back_num):
	sort = []
	len1 = len(front_num)
	len2 = len(back_num)
	if(len1 == 0):
		return back_num
	elif(len2 == 0):
		return front_num
	if(front_num[0]>back_num[0]):
		sort.append(back_num[0])
		return sort+data_merge(front_num[:],back_num[1:])
	else:
		sort.append(front_num[0])
		return sort+data_merge(front_num[1:],back_num[:])
	# merge two lists using iterations
'''
# the data length is too long, can't use the iteration



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
	# len1 = len(front_num)
	# len2 = len(back_num)
	# while(len1 > 0 and len2 > 0):
	# 	if(front_num[0] > back_num[0]):
	# 		sort.append(back_num.pop(0))
	# 		len2 = len2-1
	# 	else:
	# 		sort.append(front_num.pop(0))
	# 		len1 = len1-1
	# if(len1 == 0):
	# 	while(len2 > 0):
	# 		sort.append(back_num.pop(0))
	# 		len2 = len2-1
	# elif(len2 == 0):
	# 	while(len1 > 0):
	# 		sort.append(front_num.pop(0))
	# 		len1 = len1-1
	# del front_num
	# del back_num
	# return sort
	l = front_num+back_num
	length = len(l)
	sort = quickSort(l,0,length-1)
	return sort
	# attention, smaller number comes first

def distribution(l,queue,pipe):
	length = len(l)
	if(length < 50000):
		sort = quickSort(l,0,length-1)
		print "length small enough"
		# not split any more
	else:
		queue1 = multiprocessing.Queue()
		pipe1 = multiprocessing.Pipe()
		queue2 = multiprocessing.Queue()
		pipe2 = multiprocessing.Pipe()
		# use the queue and pipe
		front,back = data_split(l)
		pro1 = multiprocessing.Process(target = distribution,args = (front,queue1,pipe1[0]))
		pro2 = multiprocessing.Process(target = distribution,args = (back,queue2,pipe2[0]))
		pro1.start()
		pro2.start()
		print pipe1[1].recv()

		print pipe2[1].recv()
		# import pdb
		# pdb.set_trace()
		# start the process, and wait for them to terminate
		front_num = queue1.get()
		back_num = queue2.get()
		# get messages from the queue
		del queue1
		del queue2
		# delete the queue
		sort = data_merge(front_num,back_num)
		# import pdb
		# pdb.set_trace()
		# merge two rows of data ranked 
	queue.put(sort)
	pipe.send('finished')
	# print len(sort)
		# put the sorted data in the queue
		

if __name__ == '__main__':
	t1 = time.time()
	l = read_data()
	t2 = time.time()
	# read data
	queue = multiprocessing.Queue()
	pipe = multiprocessing.Pipe()
	s = multiprocessing.Process(target = distribution,args = (l,queue,pipe[0]))
	s.start()
	pipe[1].recv()
	sort = queue.get()
	t3 = time.time()
	# use the queue to send messages
	write_data(sort)
	t4 = time.time()
	print t2-t1
	print t3-t2
	print t4-t3