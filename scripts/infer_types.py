import csv, os
from datetime import datetime

p = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data','raw','DataCoSupplyChainDataset.csv')

def is_int(s):
    try:
        int(s)
        return True
    except:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except:
        return False

def is_date(s):
    fmts=['%Y-%m-%d','%Y-%m-%d %H:%M:%S','%m/%d/%Y','%m/%d/%Y %H:%M','%m/%d/%Y %H:%M:%S','%d/%m/%Y','%Y/%m/%d']
    for f in fmts:
        try:
            datetime.strptime(s, f)
            return True
        except:
            pass
    return False

counts={'int':0,'float':0,'date':0,'string':0}
with open(p,'r',encoding='utf-8',errors='replace') as f:
    reader=csv.reader(f)
    header=next(reader)
    cols=[h.strip() for h in header]
    n=len(cols)
    type_flags=[{'int':True,'float':True,'date':True} for _ in range(n)]
    non_empty=[0]*n
    for row in reader:
        for i in range(n):
            v = row[i].strip() if i < len(row) else ''
            if v=='':
                continue
            non_empty[i]+=1
            if type_flags[i].get('int') and not is_int(v):
                type_flags[i]['int']=False
            if type_flags[i].get('float') and not is_float(v):
                type_flags[i]['float']=False
            if type_flags[i].get('date') and not is_date(v):
                type_flags[i]['date']=False
    # decide
    out=[]
    for i,c in enumerate(cols):
        flags=type_flags[i]
        if flags['int']:
            t='int'
        elif flags['float']:
            t='float'
        elif flags['date']:
            t='date'
        else:
            t='string'
        out.append((i+1,c,t,non_empty[i]))

for item in out:
    print(f"{item[0]}\t{item[1]}\t{item[2]}\tNonEmpty={item[3]}")
