import psutil
from datetime import datetime
import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


es = Elasticsearch()
doc = {
    "author": "prajjwal",
    "timestamp": datetime.utcnow()
    
}
es.index(index='assignzen',doc_type="foo",body=doc)




while(True):

	pids = []
	name = [] 
	cpu_usage= []
	cpu_usage_percentage=[]
	memory_usage = []
	memory_usage_percentage =[]
	status =[]
	threads =[]
	i=0



	for process in psutil.process_iter():
		
		name.append(process.name())
		pids.append(process.pid)
	    
		memory_usage.append((process.memory_info().rss/(1024*1024),2))
		cpu_usage.append((process.cpu_percent(interval=1)+0.0)/psutil.cpu_count())
		cpu_usage_percentage.append(process.cpu_percent(interval=1)/psutil.cpu_count())
		status.append(process.status())
		memory_usage_percentage.append(round(process.memory_percent(),2))
		threads.append(process.num_threads())
		if(i>5):
			break
		i=i+1



	print("number of processes - ",i)

	data = {"PIds":pids,
	        "Name": name,
	        "CPU":cpu_usage,
	        "CPU Percentage(%)":cpu_usage_percentage,
	        "Memory Usages(MB)":memory_usage,
	        "Memory Percentage(%)": memory_usage_percentage,
	        "Status": status,
	        "Threads": threads,
	        }

	# print(data)
	process_df = pd.DataFrame(data)
	documents = process_df.to_dict(orient='records')
	bulk(es, documents, index='assignzen',doc_type='foo')
	print("Data Uploaded on ELK")

