"""Pandas calculations with native reducers and groupby aggregation."""
import pandas as pd
from common import clean, number, infer, group_sort, run

def load(path):
    df=pd.read_csv(path,dtype=str,keep_default_na=False,encoding='utf-8-sig')
    df=df.map(clean)
    names=list(df.columns)
    types={name:infer(name,df[name].tolist()) for name in names}
    print('Shape:',df.shape,'\nInput dtypes:\n',df.dtypes)
    df.info()
    nums=[c for c in names if types[c]=='numeric']
    cats=[c for c in names if c not in nums]
    if nums:
        print('Numeric describe:\n',df[nums].map(number).describe().to_string())
    if cats:
        print('Non-numeric describe:\n',df[cats].describe(include='all').to_string())
    return df,names,types

def summarize(df,names,types):
    result={}
    for name in names:
        v=df[name].dropna();n=int(v.count());missing=len(df)-n
        s=dict(count=n,missing=missing,missing_pct=100*missing/len(df) if len(df) else 0.0)
        if types[name]=='numeric':
            a=pd.to_numeric(v.map(number),errors='raise')
            s.update(mean=float(a.mean()) if n else None,min=float(a.min()) if n else None,
                     max=float(a.max()) if n else None,std=float(a.std(ddof=1)) if n>1 else None,
                     median=float(a.median()) if n else None)
        else:
            freq=v.value_counts()
            top=sorted(freq.items(),key=lambda x:(-x[1],x[0]))[:5]
            s.update(unique=int(v.nunique()),mode=top[0][0] if top else None,
                     mode_frequency=int(top[0][1]) if top else 0,
                     top5=[[a,int(b)] for a,b in top])
        result[name]=s
    return result

def groups(df,keys):
    gb=df.groupby(keys[0] if len(keys)==1 else keys,dropna=False,sort=False)
    sizes=gb.size()  # Native grouped aggregation, also identifies singleton groups.
    entries=[]
    for key,indices in gb.indices.items():
        key=key if isinstance(key,tuple) else (key,)
        key=tuple(None if pd.isna(x) else x for x in key)
        entries.append((key,indices))
    assert int(sizes.sum())==len(df)
    for key,indices in sorted(entries,key=lambda x:group_sort(x[0])):
        if len(indices)==1:
            yield key,None,tuple(df.iloc[int(indices[0])])
        else:
            yield key,df.iloc[indices],None

if __name__=='__main__':
    run('pandas',load,summarize,groups)
