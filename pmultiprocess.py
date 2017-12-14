import multiprocessing
import time

num_procs = 2
def do_work(i, message):
  print (i, "work",message ,"completed")

def worker(i, q):
  for item in iter( q.get, None ):
    do_work(i, item)
    time.sleep(1)
    q.task_done()
#  q.task_done()
  print (i, 'exit')

q = multiprocessing.JoinableQueue()
procs = []
for i in range(num_procs):
  procs.append( multiprocessing.Process(target=worker, args=(i, q)) )
  procs[-1].daemon = True

for i in range(num_procs):
  procs[i].start()

source = ['hi','there','how','are','you','doing']
for item in source:
  q.put(item)

q.join()
for p in procs:
  q.put( None )

for p in procs:
  p.join()

print ("Finished everything....")
print ("num active children:",multiprocessing.active_children())
