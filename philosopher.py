import threading
import time

  
def test(i):
    if(state[i] == 1 and state[(i+n-1)%n] != 2 and state[(i+1)%n] != 2):
        state[i] = 2
        if(s[i].locked()):
            s[i].release()
          
def take_forks(i):
    mutex.acquire()
    state[i] = 1
    test(i)
    mutex.release()
    s[i].acquire()
    
def put_forks(i):
    mutex.acquire()
    state[i] = 0
    test((i+n-1)%n)
    test((i+1)%n)
    mutex.release()

def philosopher(i):
    while(True):
        time.sleep(1)
        print "Philosopher "+str(i)+" is hungry"
        take_forks(i)
        print "Philosopher "+str(i)+" is eating"
        put_forks(i)
        print "Philosopher "+str(i) + " finished eating"
        t2 = time.time()
        if((t2 -t1)>60):
            exit()
        
global n,t1,t2
n = 5
mutex = threading.Lock()
s = []
state = []
threads = []
for i in range(0,5):
    temp = threading.Lock()
    s.append(temp)
    state.append(0)
    t = threading.Thread(target = philosopher,args = (i,))
    threads.append(t)
    
if __name__ == '__main__':
    t1 = time.time()
    for t in threads:
        t.setDaemon(True)
        t.start()
        
    