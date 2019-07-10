import time
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import concurrent.futures
import threading

num_of_clients = 30
num_of_iterations = 20
run_concurrent_test = 1

cur_iteration = 0
result = {}

def worker(cid):
	global cur_iteration, result
	mqtt_server 		= "192.168.2.110"
	mqtt_port 			= 1883

	mqtt_qos			= 1
	mqtt_retain			= False
	mqtt_keepAlive		= 60
	mqtt_cleanSession	= True 

	carduid = "7B8CF40B" # admin's carduid

	start_time = time.time()
	publish.single(
		topic 		= "{}/state/carduid".format(cid), 
		payload		= carduid, 
		qos			= mqtt_qos, 
		hostname	= mqtt_server, 
		port		= mqtt_port, 
		client_id	= "{}".format(cid)
	)
	
	msg = subscribe.simple(
		topics		= "{}/command/action".format(cid), 
		qos			= mqtt_qos,
		hostname	= mqtt_server, 
		port		= mqtt_port
	)
	duration = time.time() - start_time
	result[cur_iteration][cid] = duration

# concurrent test
def run_test(cids, num_of_clients):
	with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_clients) as executor:
		executor.map(worker, cids)

# consecutive test
def run_test2(cids):
	for cid in cids:
		worker(cid)

if __name__ == "__main__":
	cids = []
	for cid in range(num_of_clients):
		cids.append(cid+1)

	duration_sum = 0
	for i in range(num_of_iterations):
		cur_iteration = i
		result[cur_iteration] = {}
		print("{}-th iteration:".format(i+1))
		start_time = time.time()

		if run_concurrent_test:
			# run concurrent test
			run_test(cids, num_of_clients)
		else:
			# run consecutive (not concurrent) test
			run_test2(cids)

		duration = time.time() - start_time
		print("Done in {} seconds.\n" .format(duration))
		duration_sum += duration

	print("Average Duration = {}".format(duration_sum/num_of_iterations))

	# for i in range(num_of_iterations):
	# 	print("{}-th iteration:".format(i+1))
	# 	for j in range(num_of_clients):
	# 		print(result[i][j+1])

	file = open("result_30client.txt", "w+")
	for i in range(num_of_iterations):
		file.write("{}-th iteration:\n".format(i+1))
		for j in range(num_of_clients):
			file.write("{}\n".format(result[i][j+1]))
		file.write("\n")
	file.close()
