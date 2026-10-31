"""Export small readable summaries; leave full per-ad statistics out of GitHub."""
import csv,gzip,json,platform,shutil
from pathlib import Path
import pandas as pd
import polars as pl
from common import write_json

out=Path('results');out.mkdir(exist_ok=True)
for engine in ['pure_python','pandas','polars']:
    root=Path('outputs')/engine
    shutil.copyfile(root/'overall.json',out/f'{engine}_overall.json')
    shutil.copyfile(root/'manifest.json',out/f'{engine}_manifest.json')
write_json(out/'environment.json',{'python':platform.python_version(),'pandas':pd.__version__,'polars':pl.__version__})
Path('requirements.txt').write_text(f'pandas=={pd.__version__}\npolars=={pl.__version__}\n')
summary=json.loads((out/'pure_python_overall.json').read_text())
with (out/'numeric_summary.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['column','count','missing','missing_pct','mean','min','max','std','median'])
    writer.writeheader()
    for name,s in summary['columns'].items():
        if summary['types'][name]=='numeric':writer.writerow({'column':name,**s})
with (out/'missing_values.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['column','type','missing','missing_pct'])
    for name,s in summary['columns'].items():w.writerow([name,summary['types'][name],s['missing'],s['missing_pct']])
manifest=json.loads((out/'pure_python_manifest.json').read_text());names=manifest['columns']
with gzip.open('outputs/pure_python/by_page.jsonl.gz','rt') as src,(out/'page_numeric_summary.csv').open('w',newline='') as dst:
    w=csv.writer(dst);w.writerow(['page_id','rows','metric']+manifest['numeric_fields'])
    for line in src:
        r=json.loads(line)
        for name in ['estimated_spend','estimated_impressions','estimated_audience_size']:
            w.writerow([r['key'][0],r['rows'],name]+r['stats'][names.index(name)])
# Keep a few complete examples for reviewers without reproducing every record.
for name in ['by_page','by_page_ad']:
    sample=[]
    with gzip.open(f'outputs/pure_python/{name}.jsonl.gz','rt') as f:
        for _ in range(3):
            line=f.readline()
            if not line:break
            r=json.loads(line)
            r['stats']={col:dict(zip(manifest['numeric_fields'] if manifest['types'][col]=='numeric'
                                     else manifest['categorical_fields'],values))
                        for col,values in zip(names,r['stats'])}
            sample.append(r)
    write_json(out/f'{name}_examples.json',sample)
print('Exported compact review results')
