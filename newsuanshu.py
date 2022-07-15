# %%
import matplotlib.pyplot as plt
import random
# import math
from datetime import datetime
import os
import re


def renderlatex(expr):
    expr = expr.replace("*", "\\times ")
    expr = expr.replace("/", "\\div ")
    expr = "$" + expr + "$"
    return expr


def randomsample(plist, numofselections):
    NN = len(plist)
    qq = numofselections // NN
    rr = numofselections - NN * qq
    rlist = random.sample(plist, rr)
    return plist * qq + rlist


def lastnonzero(ls):
    tmpls = [i for i, e in enumerate(ls) if e != 0]
    if tmpls != []:
        ind = tmpls[-1]
    else:
        ind = -1
    return ind


qtemplates = r'''
(10,99)+(10,99)      @ 1 &    (0,)   
(0,100)-(0,100)      @ 0 & (0,)
(0,10)*(0,10)  @ 0 & (,)
(0,100)/(1,10)   @ 0 & (10,100)
'''
pattern = r"\((\d+?),(\d+?)\)(.+?)\((\d+?),(\d+?)\)"


Ncol = 4
Nrow = 7
fontsize = 10
# positions to print problems
colModifier = 0.03
rowModifier = 0.12

####################################

collist = [c/Ncol + colModifier for c in range(Ncol)]
rowlist = [r/Nrow + rowModifier for r in range(Nrow)]
totalnum = Ncol * Nrow


#################### get problem list
qtlist = qtemplates.split('\n')
qtlist = [x for x in qtlist if x != ""]

qlist = list()
qdlist = list()
qclist = list()
for qtype in qtlist:
    qp, qd = qtype.split("@")
    qd, qc = qd.split("&")
    qinfo = re.findall(pattern, qp)[0]
    qcl = re.findall(r'(\d+)\s*,', qc)
    qcr = re.findall(r',\s*(\d+)', qc)
    amin = None
    amax = None
    if len(qcl) != 0:
        amin = int(qcl[0])
    if len(qcr) != 0:
        amax = int(qcr[0])
    qlisttemp = list()
    for i in range(int(qinfo[0]), int(qinfo[1])+1):
        for j in range(int(qinfo[3]), int(qinfo[4])+1):
            question = str(i) + qinfo[2] + str(j)
            answer = eval(question)
            flag = 0
            if int(answer) != answer:
                flag = 1
            if amin is not None:
                if answer < amin:
                    flag = 1
            if amax is not None:
                if answer > amax:
                    flag = 1
            if flag == 0:
                qlisttemp.append(question)
    qlisttemp = list(set(qlisttemp))
    qlist.append(qlisttemp)
    qdlist.append(int(qd))
    # qclist.append(qc)

Ntype = len(qdlist)

##############   compute distribution
T = sum(qdlist)
for i in range(len(qdlist)):
    qdlist[i] = int(qdlist[i] / T * totalnum)
err = totalnum - sum(qdlist)
ind = lastnonzero(qdlist)
if ind >= 0:
    qdlist[ind] = qdlist[ind] + err

############### get list
plist = list()
for i in range(Ntype):
    plist += randomsample(qlist[i], qdlist[i])
random.shuffle(plist)

################# print
fig, ax = plt.subplots(figsize=(8.5, 11), dpi=300)
for i in range(Nrow):
    for j in range(Ncol):
        ax.text(collist[j], rowlist[i], renderlatex(plist[i*Ncol+j])+"=",
                fontsize=fontsize)
plt.axis('off')
now = datetime.now()
assfolder = './math_calculation/'
if not os.path.isdir(assfolder):
    os.mkdir(assfolder)
fdatepath = now.strftime('%y%m%d/')
if not os.path.isdir(assfolder+fdatepath):
    os.mkdir(assfolder+fdatepath)
fname = now.strftime('%H%M%S.png')
plt.savefig(assfolder+fdatepath+fname, pad_inches=0, format='png',
            bbox_inches='tight')