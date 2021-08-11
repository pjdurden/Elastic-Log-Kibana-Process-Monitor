try:
    import random
    from datetime import date
    from datetime import datetime
    import datetime
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
    from elasticsearch import helpers
    import json
    from time import sleep
    from queue import Queue
    import hashlib
    import base64
    print("All Modules ok ")
except Exception as e:
    print("Error : {} ".format(e))

# ------------ Variable -----------------------------
global NUM_OF_RECORDS
global ENDPOINT
global ELK_USERNAME
global ELK_PASSWORD
global IndexName
global sensor_queue

IndexName = 'iot_sensor'
ENDPOINT = 'http://localhost:9200/'
sensor_queue = Queue(maxsize=10)
# ------------------------------------------------


class DateTime(object):
    @staticmethod
    def get():
        return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def getTime():
        return datetime.datetime.utcnow().strftime("%H:%M:%S")

    @staticmethod
    def getDate():
        return datetime.datetime.utcnow().strftime("%Y-%m-%d")


class MyHasher(object):
    def __init__(self, key):
        self.key = key

    def get(self):
        keys = str(self.key).encode("UTF-8")
        keys = base64.b64encode(keys)
        keys = keys.decode("UTF-8")
        return keys



class DateGenerator(object):

    __slots__ = ["num_of_record", "payload"]

    def __init__(self, num_of_record=2):
        self.num_of_record = num_of_record
        self.payload = {
            "Mem-used":   random.randint(250, 500),
            "Disk_read":random.randint(1024, 8192),
            "Disk_writ":0,
            "Mem_free":random.randint(0, 1000),
            "Mem_buff":0,
            "Mem_cach":' ',
            "CPU_idl": random.randint(0, 100),
            "CPU_usr":random.randint(13, 72),
            "CPU_sys":100 - (random.randint(13, 72) + random.randint(0, 100)),
            "CPU_stl":0,
            "CPU_wai":0,
            "Net_recv":random.randint(112, 784),
            "Net_send":random.randint(112, 476),
            "Version":'0.0.0',
            "uptime":random.randint(1, 100),
            'proc_run':random.randint(1, 10),
            'proc_blk': random.randint(1, 10),
            'proc_new':random.randint(1, 10),
            '1m':random.random(),
            '5m':random.random(),
            '15m':random.random(),
            'temperature':random.randint(20, 60),
            'humidity':random.randint(20, 80),
        }

    def get(self):

        _hasher = MyHasher(key=str(self.payload.get("date_time")))
        key =_hasher.get()
        _ = {
            '_index': IndexName,
            '_id': key,
            '_source': self.payload
        }
        return _

class ELKGenerator(object):

    @staticmethod
    def get(records):
        for record in records:
            yield {
                "_index": record.get("_index"),
                '_id': record.get("key"),
                '_source': record.get("_source")
            }


class ELKBulk(object):

    def __init__(self):
        self.es = Elasticsearch(timeout=600, hosts=ENDPOINT)

    def put(self, array=[]):
        try:
            res = helpers.bulk(self.es, ELKGenerator.get(array))
            return True
        except Exception as e:
            print("Error : {} ".format(e))

def main():
    _generator = DateGenerator(num_of_record=1)
    _eshelper = ELKBulk()

    while True:

        if sensor_queue.full():         # CHeck is Queue is Full MAx size is 10
            _bulkdata = []

            while not sensor_queue.empty():
                _bulkdata.append(sensor_queue.get())

            # Queue is Empty
            # we have 10 Records to Push
            _re = _eshelper.put(array=_bulkdata)
            print("Data on ELK ")


        # Put the Sensor Data In Queue
        _record =_generator.get()
        sensor_queue.put(_record)
        print("Data on queue ")
        sleep(3)


if __name__ == "__main__":
    main()
