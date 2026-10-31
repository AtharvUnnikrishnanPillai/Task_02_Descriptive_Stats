"""Known-answer checks for empty, missing, singleton, and multi-row groups."""
import contextlib,csv,io,tempfile,unittest
from pathlib import Path
import pure_python_stats as pure
import pandas_stats as pandas
import polars_stats as polars
from common import singleton
from compare_results import compare

class TestStats(unittest.TestCase):
    def test_empty_and_singleton_numeric_groups(self):
        import pandas as pd
        import polars as pl
        names=['amount'];types={'amount':'numeric'}
        cases=[([],pd.DataFrame({'amount':pd.Series([],dtype=object)}),
                pl.DataFrame({'amount':[]},schema={'amount':pl.String})),
               ([(None,)],pd.DataFrame({'amount':[None]}),
                pl.DataFrame({'amount':[None]},schema={'amount':pl.String})),
               ([('7',)],pd.DataFrame({'amount':['7']}),
                pl.DataFrame({'amount':['7']},schema={'amount':pl.String}))]
        for a,b,c in cases:
            results=[pure.summarize(a,names,types),pandas.summarize(b,names,types),polars.summarize(c,names,types)]
            for r in results[1:]:compare(results[0],r)
            self.assertIsNone(results[0]['amount']['std'])
        self.assertEqual(results[0]['amount']['mean'],7)

    def test_three_engines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'test.csv'
            with path.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['page_id','ad_id','amount','label','empty','mixed','zero'])
                w.writerows([['001','a','0','b','','4','0'],['001','a','2','a','NA','bad','0'],
                             ['001','b','4','b','null','','0'],['002','c','','a','','','0'],
                             ['','d','$1,000','a','','','0']])
            outputs=[];group_outputs=[]
            for engine in [pure,pandas,polars]:
                with contextlib.redirect_stdout(io.StringIO()):
                    data,names,types=(engine.loader(path) if engine is pure else engine.load(path))
                stats=engine.summarize(data,names,types)
                outputs.append(stats)
                levels=[]
                for keys in [['page_id'],['page_id','ad_id']]:
                    groups=[]
                    for key,g,row in engine.groups(data,keys):
                        s=singleton(row,names,types) if g is None or len(g)==1 else engine.summarize(g,names,types)
                        groups.append({'key':list(key),'stats':s})
                    levels.append(groups)
                group_outputs.append(levels)
            for output in outputs[1:]:compare(outputs[0],output)
            for output in group_outputs[1:]:compare(group_outputs[0],output)
            s=outputs[0]
            self.assertEqual(s['amount']['mean'],251.5)
            self.assertEqual(s['amount']['median'],3)
            self.assertEqual(s['empty']['count'],0)
            self.assertEqual(s['zero']['std'],0)
            page=next(x for x in group_outputs[0][0] if x['key']==['001'])
            self.assertEqual(page['stats']['amount']['std'],2)
            self.assertEqual(page['stats']['amount']['median'],2)
            pair=next(x for x in group_outputs[0][1] if x['key']==['001','a'])
            self.assertAlmostEqual(pair['stats']['amount']['std'],2**.5)
            self.assertEqual(pair['stats']['label']['mode'],'a')

if __name__=='__main__':unittest.main()
