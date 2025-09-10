# %%
import matplotlib.pyplot as plt
import numpy as np
import random, os, re
from datetime import datetime
from pathlib import Path


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


def genqvault(qtemplates, N=10):
    qtlist = qtemplates.split('\n')
    qtlist = [x for x in qtlist if x != ""]
    qlist = list()
    qdlist = list()
    qclist = list()
    plist = list()
    M = len(qtlist)
    for qtype in qtlist:
        qp, qd = qtype.split("@")
        qd, qc = qd.split("&")
        qcl = re.findall(r'(\d+)\s*,', qc)
        qcr = re.findall(r',\s*(\d+)', qc)
        amin = None
        amax = None
        if len(qcl) != 0:
            amin = int(qcl[0])
        if len(qcr) != 0:
            amax = int(qcr[0])
        qdlist.append(qd)
        qlist.append(qp)
        qclist.append((amin, amax))
    qdlist = np.array(qdlist, dtype=int)
    pp = qdlist/qdlist.sum()
    # print(pp)
    rqdlist = np.random.choice(list(range(M)), size=N, p=pp)
    # print(rqdlist)
    # print(qlist)
    for i in rqdlist:
        amin = qclist[i][0]
        amax = qclist[i][1]
        # for _ in range(N):
        flag = 1
        while (flag):
            prob = generateq(qlist[i])
            ans = eval(prob)
            if (ans != int(ans)):
                continue
            if amin is not None:
                if ans < amin:
                    continue
            if amax is not None:
                if ans > amax:
                    continue
            flag = 0
        plist.append(prob)
        # print(i, qlist[i], prob)
    # print(plist)
    return plist


# def genproblemlist(qlist, qdlist, totalnum):
#     Ntype = len(qdlist)
#     #    compute distribution
#     T = sum(qdlist)
#     for i in range(len(qdlist)):
#         qdlist[i] = int(qdlist[i] / T * totalnum)
#     err = totalnum - sum(qdlist)
#     ind = lastnonzero(qdlist)
#     if ind >= 0:
#         qdlist[ind] = qdlist[ind] + err
#     #     get list
#     plist = list()
#     for i in range(Ntype):
#         plist += randomsample(qlist[i], qdlist[i])
#     random.shuffle(plist)
#     return plist


def replacenumber(qtem):
    # print(qtem)
    low, high = re.findall(r'\[(\d+?),(\d+?)\]', qtem[0])[0]
    return str(random.randint(int(low), int(high)))


def generateq(ptem):
    # tp = r'\[\d+?,\d+?\]'
    # return re.sub(tp, replacenumber, ptem)
    numdict = random_pattern(num_pattern)

    pattern = re.compile("|".join(re.escape(k) for k in numdict))

    # Replace using a lambda that looks up each match in the dictionary
    result = pattern.sub(lambda m: numdict[m.group(0)], ptem)
    return result

# def random_pattern(num_pattern, N=100):
#     nums = [num for num in num_pattern.split('\n') if len(num)!=0]
#     numdict = {}
#     for num in nums:
#         v, l, h = re.findall(r'(\w+)=\[(\d+?),(\d+?)\]', num)[0]
#         numdict[v]=str(random.randint(int(l), int(h)))
#         numdict['b'+v] = str(N-int(numdict[v]))
#     return numdict

def random_pattern(num_pattern):
    nums = [num for num in num_pattern.split('\n') if len(num)!=0]
    numdict = {}

    local_vars = {'random': random}
    for _num in nums:
        v = _num.split('=')[0]
        exec(_num, {}, local_vars)
        numdict[v]=str(local_vars[v])
        # exec(v+'='+numdict[v])
        # numdict['b'+v] = str(N-int(numdict[v]))
    return numdict


# %%
#  configuration
num_pattern = r'''
A1=random.randint(1,29)
A2=random.randint(10,99)
B1=random.randint(1,19)
B2=random.randint(10,99)
B3=10-B1
C1=random.randint(1,9)
C2=random.randint(10,99)
bA2=C1*10-A2 if C1*10>A2 else C1*100-A2
bA3=C1*10+A2
'''

qtemplates_v2 = r'''
(A1-B1)-C1 @1 &(0,)
(A1-B1)+C1 @1 &(0,)
(A1+B1)-C1 @1 &(0,)
(A1+B1)+C1 @1 &(0,)
C1-(A1-B1) @1 &(0,)
C1+(A1-B1) @1 &(0,)
C1-(A1+B1) @1 &(0,)
C1+(A1+B1) @1 &(0,)
A1+B1+C1 @1 &(0,)
A1+B1-C1 @1 &(0,)
A1-B1+C1 @1 &(0,)
A1-B1-C1 @1 &(0,)
'''

# qtemplates_v2 = r'''
# A2/B1 @1 &(0,)
# A1*B1 @1 &(0,)
# '''

# qtemplates_v2 = r'''
# (A2-B2)-C2 @1 &(0,)
# (A2-B2)+C2 @1 &(0,)
# (A2+B2)-C2 @1 &(0,)
# (A2+B2)+C2 @1 &(0,)
# C2-(A2-B2) @1 &(0,)
# C2+(A2-B2) @1 &(0,)
# C2-(A2+B2) @1 &(0,)
# C2+(A2+B2) @1 &(0,)
# A2+B2+C2 @1 &(0,)
# A2+B2-C2 @1 &(0,)
# A2-B2+C2 @1 &(0,)
# A2-B2-C2 @1 &(0,)
# '''
# qtemplates_v2 = r'''
# bA3*C2-A2*C2  @1 &(0,)
# C2*bA3-A2*C2  @1 &(0,)
# bA3*C2-C2*A2  @1 &(0,)
# C2*bA3-C2*A2  @1 &(0,)
# A2*C2+bA2*C2 @1 &(0,)
# A2*C2+C2*bA2 @1 &(0,)
# C2*A2+bA2*C2 @1 &(0,)
# C2*A2+C2*bA2 @1 &(0,)
# '''

# qtemplates_v2 = r'''
# (A2-B2)*C2 @1 &(0,)
# (A2+A2)*C2 @1 &(0,)
# C2*(A2-B2) @1 &(0,)
# C2*(A2+B2) @1 &(0,)
# A2*C2+B2*C2 @1 &(0,)
# A2*C2-B2*C2  @1 &(0,)
# C2*A2+B2*C2 @1 &(0,)
# C2*A2-B2*C2  @1 &(0,)
# A2*C2+A2*B2 @1 &(0,)
# A2*C2-A2*B2  @1 &(0,)
# C2*A2+A2*B2 @1 &(0,)
# C2*A2-A2*B2  @1 &(0,)
# A2*C2+bA2*C2 @2 &(0,)
# A2*C2+C2*bA2 @2 &(0,)
# C2*A2+bA2*C2 @2 &(0,)
# C2*A2+C2*bA2 @2 &(0,)
# '''

# qtemplates = r'''
# ([10,99]*[10,99]) +[1,10]     @ 0     &    (0,)
# [10,99]*[100,999]      @ 0     & (0, )
# [1,10]+[10,99]      @ 0     & (0, 99)
# [10,99]-[1,99]      @ 0     & (0, )
# [10,99]-[1,9]        @ 0     & (0,100)
# [10,89]+[1,9]       @ 0     & (0,100)
# [10,99]+[1,99]        @ 0     & (50,100)
# [10,99]-[1,99]        @ 0     & (10,100)
# [100,999]*[100,999]   @ 0      & (0,)
# [10,999]/[3,10]       @ 0     & (,)
# [0,100]/[1,10]       @ 0     & (1,1)
# '''
# qtemplates = r'''
# [1,20]+[1,20]+[1,20]    @0   & (0,)
# [1,30]+[1,30]-[1,30]    @1   & (0,)
# [1,30]-[1,30]+[1,30]    @1   & (0,)
# [1,30]-[1,30]-[1,30]    @1   & (0,)
# [1,30]+([1,30]-[1,30])    @1   & (0,)
# [1,30]-([1,30]+[1,30])    @1   & (0,)
# [1,30]-([1,30]-[1,30])    @1   & (0,)
# '''

# qtemplates = r'''
# [10,40] + [1,9]*[1,9]  @1 &(0,)
# [1,9]*[1,9]+[10,40]   @1 &(0,)
# [10,40] - [1,9]*[1,9]  @1 &(0,)
# [1,9]*[1,9]-[10,40]   @1 &(0,)
# '''

pattern = r"\((\d+?),(\d+?)\)(.+?)\((\d+?),(\d+?)\)"

# qlist, qdlist = genqvault(qtemplates)


# %%
Ncol = 4
Nrow = 8
fontsize = 10
# positions to print problems
colModifier = 0.03
rowModifier = 0.1

####################################
collist = [c/Ncol + colModifier for c in range(Ncol)]
rowlist = [r/Nrow + rowModifier for r in range(Nrow)]
totalnum = Ncol * Nrow

#################### get problem list
# plist = genproblemlist(qlist, qdlist, totalnum=totalnum)
plist = genqvault(qtemplates_v2, Ncol*Nrow)
################# print
fig, ax = plt.subplots(figsize=(8.5, 11), dpi=300)
for i in range(Nrow):
    for j in range(Ncol):
        # print(plist[i*Ncol+j])
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
# %%

# %%
