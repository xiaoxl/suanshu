import matplotlib.pyplot as plt
import random
import math
from datetime import datetime
import os
import re


qtemplates = r'''
(0,1)+(0,100)      @ 1
(0,100)-(0,100)      @ 1
(0,10)\\times(0,10)  @ 1
(0,100)\\div(1,10)   @ 1
'''

pattern = r"\((\d+?),(\d+?)\)(.+?)\((\d+?),(\d+?)\)"

qtlist = qtemplates.split('\n')
qtlist = [x for x in qtlist if x != ""]

qlist = list()
qdlist = list()

for qtype in qtlist:
    qp, qd = qtype.split("@")
    qinfo = re.findall(pattern, qp)[0]
    qlisttemp = list()
    for i in range(int(qinfo[0]), int(qinfo[1])+1):
        for j in range(int(qinfo[3]), int(qinfo[4])+1):
            question = str(i) + qinfo[2] + str(j)
            qlisttemp.append(question)
    qlisttemp = list(set(qlisttemp))
    qlist.append(qlisttemp)
    qdlist.append(qd)







re.findall(pattern, '(0,10)\\times(0,10)')