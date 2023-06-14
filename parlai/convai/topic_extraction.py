import random
import os
import linecache
import yaml
def topic_extract():
    topic_result=[]
    myfile = open('/home/intern/seungjun/ParlAI/parlai/convai/topic.txt')
    total_len = len(myfile.readlines())
    random_num = random.sample(range(0, total_len),1)
    for i in random_num:
        per_data = linecache.getline('/home/intern/seungjun/ParlAI/parlai/convai/topic.txt',i).strip()
        topic_result.append(per_data)
    return topic_result