import sys
fn = sys.argv[1]
with open (fn, "r") as myfile:
	data = myfile.readlines()
ids = []
for line in data:
	if line[:4] == "http":
		i = line.rfind('/')
		line.rstrip()
		ids.append(line[i+1:].replace('\n','') )
#print (ids)
for id in ids:
	print(id)
