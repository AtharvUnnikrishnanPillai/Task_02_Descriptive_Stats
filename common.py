"""Shared input conventions and output formatting; no multi-row statistics."""
import argparse
import gzip
import hashlib
import json
import math
from datetime import date
from pathlib import Path
from time import perf_counter

MISSING = {'', 'na', 'n/a', 'null', 'none', 'nan'}
NUMERIC_FIELDS = ['count','missing','missing_pct','mean','min','max','std','median']
CATEGORY_FIELDS = ['count','missing','missing_pct','unique','mode','mode_frequency','top5']

def clean(value):
    if value is None:
        return None
    text = str(value).strip()
    return None if text.casefold() in MISSING else text

def number(value):
    if value is None:
        return None
    text = value.replace(',', '').removeprefix('$')
    if text.startswith('(') and text.endswith(')'):
        text = '-' + text[1:-1]
    try:
        n = float(text)
        return n if math.isfinite(n) else None
    except ValueError:
        return None

def infer(name, values):
    values = [x for x in values if x is not None]
    if not values:
        return 'empty'
    if name.lower().endswith('_id') or name == 'illuminating_scored_message':
        return 'categorical'
    if all(number(x) is not None for x in values):
        return 'numeric'
    try:
        if all(date.fromisoformat(x).isoformat() == x for x in values):
            return 'date'
    except ValueError:
        pass
    return 'categorical'

def singleton(row, names, types):
    """Exact singleton identities; no estimated variance for a single observation."""
    result = {}
    for name, value in zip(names, row):
        count = int(value is not None)
        common = dict(count=count, missing=1-count, missing_pct=float(100*(1-count)))
        if types[name] == 'numeric':
            n = number(value)
            common.update(mean=n, min=n, max=n, std=None, median=n)
        else:
            common.update(unique=count, mode=value, mode_frequency=count,
                          top5=[[value, 1]] if count else [])
        result[name] = common
    return result

def group_sort(key):
    return tuple((x is not None, x or '') for x in key)

def pack(stats, names, types):
    return [[stats[name][f] for f in (NUMERIC_FIELDS if types[name]=='numeric' else CATEGORY_FIELDS)]
            for name in names]

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')

def run(engine, loader, summarizer, grouper):
    parser = argparse.ArgumentParser(description=f'{engine}: whole-dataset and grouped descriptive statistics')
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--out-dir', type=Path)
    args = parser.parse_args()
    out = args.out_dir or Path('outputs') / engine
    out.mkdir(parents=True, exist_ok=True)
    start = perf_counter()
    data, names, types = loader(args.csv_path)
    for key in ['page_id','ad_id']:
        if key not in names:
            raise ValueError(f'Required Task 2 grouping column missing: {key}')
    total = summarizer(data, names, types)
    with args.csv_path.open('rb') as f:
        sha = hashlib.file_digest(f,'sha256').hexdigest()
    summary = dict(rows=len(data), column_count=len(names), types=types, columns=total, sha256=sha)
    write_json(out/'overall.json',summary)
    # Fixed global types prevent an all-null subgroup changing a numeric column's type.
    manifest = dict(columns=names, types=types, numeric_fields=NUMERIC_FIELDS,
                    categorical_fields=CATEGORY_FIELDS, groups={})
    for keys, filename in [(['page_id'],'by_page.jsonl.gz'), (['page_id','ad_id'],'by_page_ad.jsonl.gz')]:
        count = singles = 0
        with gzip.open(out/filename,'wt',encoding='utf-8',compresslevel=1) as handle:
            for key, group, row in grouper(data, keys):
                n = len(group) if group is not None else 1
                stats = singleton(row,names,types) if n == 1 else summarizer(group,names,types)
                record = {'key':list(key),'rows':n,'stats':pack(stats,names,types)}
                handle.write(json.dumps(record, separators=(',',':'), ensure_ascii=False,allow_nan=False)+'\n')
                count += 1
                singles += n == 1
        manifest['groups'][filename] = dict(keys=keys, count=count, singleton_groups=singles)
        print(engine,filename,count,'groups',flush=True)
    write_json(out/'manifest.json',manifest)
    write_json(out/'runtime.json',{'engine':engine,'elapsed_seconds':perf_counter()-start})
    print(engine,'complete; outputs:',out,flush=True)
