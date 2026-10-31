"""Polars expression reducers and native group_by aggregation."""
import polars as pl
from common import clean, number, infer, group_sort, run

def load(path):
    df=pl.read_csv(path,infer_schema=False,encoding='utf8')
    df=df.with_columns(pl.col(c).map_elements(clean,return_dtype=pl.String) for c in df.columns)
    names=df.columns
    types={name:infer(name,df[name].to_list()) for name in names}
    print('Shape:',df.shape,'\nSchema:',df.schema)
    return df,names,types

def summarize(df,names,types):
    result={}
    for name in names:
        v=df[name].drop_nulls();n=len(v);missing=df.height-n
        s=dict(count=n,missing=missing,missing_pct=100*missing/df.height if df.height else 0.0)
        if types[name]=='numeric':
            a=pl.DataFrame({'value':[number(x) for x in v]},schema={'value':pl.Float64})
            row=a.select(pl.col('value').mean().alias('mean'),pl.col('value').min().alias('min'),
                         pl.col('value').max().alias('max'),pl.col('value').std(ddof=1).alias('std'),
                         pl.col('value').median().alias('median')).row(0,named=True)
            s.update(row)
        else:
            freq=v.alias('value').value_counts().sort(['count','value'],descending=[True,False]).head(5)
            top=[[r['value'],r['count']] for r in freq.to_dicts()]
            s.update(unique=v.n_unique(),mode=top[0][0] if top else None,
                     mode_frequency=top[0][1] if top else 0,top5=top)
        result[name]=s
    return result

def groups(df,keys):
    # Native grouped count and index aggregation; rows are not regrouped in Python.
    indexed=df.with_row_index('__row_index')
    grouped=indexed.group_by(keys).agg(pl.len().alias('__n'),pl.col('__row_index'))
    entries=[]
    for rec in grouped.iter_rows(named=True):
        entries.append((tuple(rec[k] for k in keys),rec['__row_index']))
    for key,indices in sorted(entries,key=lambda x:group_sort(x[0])):
        if len(indices)==1:
            yield key,None,df.row(indices[0])
        else:
            yield key,df[indices],None

if __name__=='__main__':
    run('polars',load,summarize,groups)
