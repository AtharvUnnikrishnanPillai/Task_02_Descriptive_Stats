"""Stream every group's statistics and compare all three approaches."""
import argparse
import gzip
import itertools
import json
import math
from pathlib import Path
from common import write_json

def compare(a,b,path='root'):
    if isinstance(a,dict):
        if not isinstance(b,dict) or a.keys()!=b.keys():raise AssertionError(path+' keys')
        return sum(compare(a[k],b[k],path+'.'+k) for k in a)
    if isinstance(a,list):
        if not isinstance(b,list) or len(a)!=len(b):raise AssertionError(path+' length')
        return sum(compare(x,y,path+f'[{i}]') for i,(x,y) in enumerate(zip(a,b)))
    if isinstance(a,int) and isinstance(b,int):
        if a!=b:raise AssertionError((path,a,b))
    elif isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)):
        if not math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9):raise AssertionError((path,a,b))
    elif a!=b:raise AssertionError((path,a,b))
    return 1

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path('outputs'))
    p.add_argument('--out',type=Path,default=Path('results/comparison.json'))
    args=p.parse_args();roots=[args.root/x for x in ['pure_python','pandas','polars']]
    overall=[json.loads((x/'overall.json').read_text()) for x in roots]
    leaves=sum(compare(overall[0],x) for x in overall[1:])
    manifests=[json.loads((x/'manifest.json').read_text()) for x in roots]
    for m in manifests[1:]:compare(manifests[0],m)
    counts={}
    for filename in ['by_page.jsonl.gz','by_page_ad.jsonl.gz']:
        handles=[gzip.open(x/filename,'rt',encoding='utf-8') for x in roots]
        count=0
        try:
            for lines in itertools.zip_longest(*handles):
                if any(x is None for x in lines):raise AssertionError('Unequal group counts')
                records=[json.loads(line) for line in lines]
                leaves+=sum(compare(records[0],r) for r in records[1:])
                count+=1
        finally:
            for h in handles:h.close()
        counts[filename]=count
        print(filename,count,'groups PASS',flush=True)
    report={'status':'PASS','group_counts':counts,'pairwise_leaf_checks':leaves,
            'relative_tolerance':1e-9,'absolute_tolerance':1e-9,'input_sha256':overall[0]['sha256']}
    args.out.parent.mkdir(parents=True,exist_ok=True);write_json(args.out,report);print(report)

if __name__=='__main__':main()
