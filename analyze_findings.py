"""Substantive findings: keep estimates, currencies and exact mention strings distinct."""
import argparse,ast,csv
from collections import Counter,defaultdict
from pathlib import Path
from common import clean,number,write_json

def analyze(path):
    pages=defaultdict(lambda:{'rows':0,'usd_rows':0,'usd_estimated_spend':0.0,'currencies':set(),'bylines':Counter()})
    currencies=Counter();totals=defaultdict(float);dates=Counter();mentions=Counter();platforms=Counter()
    malformed=Counter();empty=Counter();labels=Counter();region_usd=defaultdict(float);pairs=Counter();n=0
    with path.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            n+=1;p=pages[row['page_id']];p['rows']+=1;p['currencies'].add(row['currency'])
            if clean(row['bylines']) is not None:p['bylines'][row['bylines']]+=1
            currencies[row['currency']]+=1;pairs[(row['page_id'],row['ad_id'])]+=1
            amount=number(clean(row['estimated_spend']))
            if amount is not None:
                totals[row['currency']]+=amount
                if row['currency']=='USD':p['usd_rows']+=1;p['usd_estimated_spend']+=amount
            dates[row['ad_creation_time'][:7]]+=1
            for col,counter in [('illuminating_mentions',mentions),('publisher_platforms',platforms)]:
                try:
                    v=ast.literal_eval(row[col])
                    if not isinstance(v,list) or not all(isinstance(x,str) for x in v):raise ValueError()
                    counter.update(set(v))
                    if not v:empty[col]+=1
                except (ValueError,SyntaxError,TypeError):malformed[col]+=1
            for col in ['delivery_by_region','demographic_distribution']:
                try:
                    v=ast.literal_eval(row[col])
                    if not isinstance(v,dict):raise ValueError()
                    if not v:empty[col]+=1
                    for key,values in v.items():
                        if not isinstance(values,dict):raise ValueError()
                        for metric in ['spend','impressions']:
                            if metric in values and not isinstance(values[metric],(int,float)):raise ValueError()
                        if col=='delivery_by_region' and row['currency']=='USD':region_usd[key]+=values.get('spend',0)
                except (ValueError,SyntaxError,TypeError):malformed[col]+=1
            labels.update(k for k,v in row.items() if k.endswith('_illuminating') and v=='1')
    top=[]
    for pid,p in sorted(pages.items(),key=lambda item:(-item[1]['usd_estimated_spend'],item[0]))[:10]:
        top.append({'page_id':pid,'rows':p['rows'],'usd_rows':p['usd_rows'],
                    'usd_estimated_spend':p['usd_estimated_spend'],
                    'most_frequent_byline':p['bylines'].most_common(1)[0][0] if p['bylines'] else None})
    return {'rows':n,'pages':len(pages),'page_ad_pairs':len(pairs),
            'repeated_pairs':sum(c>1 for c in pairs.values()),
            'mixed_currency_pages':sum(len(p['currencies'])>1 for p in pages.values()),
            'currencies':dict(currencies),'estimated_spend_by_currency':dict(totals),
            'top_usd_pages':top,'creation_month_counts':dict(sorted(dates.items())),
            'exact_mentions':dict(mentions.most_common()),'platform_record_counts':dict(platforms),
            'positive_labels':dict(labels),'structured_parse_errors':dict(malformed),
            'empty_structures':dict(empty),
            'regional_usd_estimated_spend_top10':dict(sorted(region_usd.items(),key=lambda x:-x[1])[:10])}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv_path',type=Path)
    args=p.parse_args();Path('results').mkdir(exist_ok=True)
    write_json(Path('results/findings.json'),analyze(args.csv_path));print('Saved results/findings.json')
