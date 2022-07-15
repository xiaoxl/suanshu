# %%
import matplotlib.pyplot as plt
import random
import math
from datetime import datetime
import os
import re

from sympy import Q


def randomsample(plist, numofselections):
    NN = len(plist)
    qq = numofselections // NN
    rr = numofselections - NN * qq
    rlist = random.sample(plist, rr)
    return plist * qq + rlist

# %%
# pl = [1,2,3,4,5,6]
# rl = randomsample(pl, 15)
# print(rl)

# %%
# upper bound for the operations
Nadd = 100
Ntimes = 10
multiplicationcap = 100
# distribution for different types
Tadd, Tminus, Ttimes, Tq = 1, 0, 0, 0
# positions to print problems
Ncol = 4
Nrow = 7
fontsize = 10
# positions to print problems
colModifier = 0.03
rowModifier = 0.12

collist = [c/Ncol + colModifier for c in range(Ncol)]
rowlist = [r/Nrow + rowModifier for r in range(Nrow)]

# generate the valut
qadd = list()
qminus = list()
qtimes = list()
qq = list()
for i in range(10, 100):
    for j in range(10, 100):
        if i+j <= 200:
            qadd.append(str(i)+'+'+str(j))
        if i >= j:
            qminus.append(str(i)+'-'+str(j))
for i in range(Ntimes+1):
    for j in range(Ntimes+1):
        if i*j <= multiplicationcap:
            qtimes.append(str(i)+'\\times'+str(j))
for i in range(1, 10):
    for j in range(1, 10):
        qq.append(str(i*j)+'\\div'+str(i))
qadd = list(set(qadd))
qtimes = list(set(qtimes))
qq = list(set(qq))

# generate this specific problem list
T = Tadd + Tminus + Ttimes + Tq
N = Ncol * Nrow
NTadd = math.floor(N * Tadd / T)
NTminus = math.floor(N * Tminus / T)
NTtimes = math.floor(N * Ttimes / T)
NTq = N - NTadd - NTminus - NTtimes

plistadd = randomsample(qadd, NTadd)
plistminus = randomsample(qminus, NTminus)
plisttimes = randomsample(qtimes, NTtimes)
plistq = randomsample(qq, NTq)
plist = plistadd + plistminus + plisttimes + plistq
random.shuffle(plist)

# print the problem list
fig, ax = plt.subplots(figsize=(8.5, 11), dpi=300)
for i in range(Nrow):
    for j in range(Ncol):
        ax.text(collist[j], rowlist[i], '$'+plist[i*Ncol+j]+'=$',
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

# %%
