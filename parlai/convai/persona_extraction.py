import random
import os
import linecache

def persona_extract():
    persona_result=[]
    myfile = open('/home/intern/seungjun/ParlAI/parlai/convai/persona.txt')
    total_len = len(myfile.readlines())
    random_num = random.sample(range(0, total_len),8)

    for i in random_num:
        per_data = linecache.getline('/home/intern/seungjun/ParlAI/parlai/convai/persona.txt',i).strip()
        persona_result.append(per_data)
    return persona_result