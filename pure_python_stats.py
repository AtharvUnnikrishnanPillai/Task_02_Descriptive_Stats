"""Independent standard-library calculations, including dictionary-based grouping."""
import csv
import math
from collections import Counter, defaultdict
from common import clean, number, infer, group_sort, run

def load(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.reader(f)
        names=next(reader)
        if len(set(names)) != len(names):
            raise ValueError('Duplicate column names')
        rows=[]
        for i,row in enumerate(reader,2):
            if len(row)!=len(names):
                raise ValueError(f'Wrong field count at record {i}')
            rows.append(tuple(clean(x) for x in row))
    types={name:infer(name,[r[i] for r in rows]) for i,name in enumerate(names)}
    return rows,names,types

def summarize(rows,names,types):
    result={}
    for i,name in enumerate(names):
        values=[r[i] for r in rows if r[i] is not None]
        n=len(values); missing=len(rows)-n
        s=dict(count=n,missing=missing,missing_pct=100*missing/len(rows) if rows else 0.0)
        if types[name]=='numeric':
            a=sorted(number(v) for v in values)
            mean=math.fsum(a)/n if n else None
            s.update(mean=mean,min=a[0] if n else None,max=a[-1] if n else None,
                     std=math.sqrt(math.fsum((x-mean)**2 for x in a)/(n-1)) if n>1 else None,
                     median=(a[n//2] if n%2 else (a[n//2-1]+a[n//2])/2) if n else None)
        else:
            freq=Counter(values)
            top=sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:5]
            s.update(unique=len(freq),mode=top[0][0] if top else None,
                     mode_frequency=top[0][1] if top else 0,top5=[list(x) for x in top])
        result[name]=s
    return result

def groups(rows,keys):
    # Load header indices from the source schema assigned by main's loader.
    indices=[NAMES.index(k) for k in keys]
    grouped=defaultdict(list)
    for row in rows:
        grouped[tuple(row[i] for i in indices)].append(row)
    for key in sorted(grouped,key=group_sort):
        group=grouped[key]
        yield key,group,group[0] if len(group)==1 else None

NAMES=[]
def loader(path):
    global NAMES
    rows,NAMES,types=load(path)
    return rows,NAMES,types

if __name__=='__main__':
    run('pure_python',loader,summarize,groups)
