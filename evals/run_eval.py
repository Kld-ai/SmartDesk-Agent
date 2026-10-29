"""Run A/B cases. Note: substring checks are only a lightweight baseline grader."""
import argparse,asyncio,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from smartdesk.agent import SmartDesk
async def main(mock):
    cases=json.loads((Path(__file__).parent/'cases.json').read_text())
    rows=[]
    for cfg in ('A','B'):
        for case in cases:
            try:
                out=await SmartDesk(mock=mock,config=cfg).run(case['q'])
                answer=out['answer']; passed=case['expect'].lower() in answer.lower()
                rows.append({'config':cfg,'case_id':case['id'],'passed':int(passed),'steps':out['steps'],'tool_calls':out['tool_calls'],'question':case['q'],'answer':answer,'trace':json.dumps(out['trace'])})
            except Exception as e:
                rows.append({'config':cfg,'case_id':case['id'],'passed':0,'steps':0,'tool_calls':0,'question':case['q'],'answer':str(e),'trace':'[]'})
    target=Path(__file__).parent/'results.csv'
    with target.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    for cfg in ('A','B'):
        subset=[r for r in rows if r['config']==cfg]
        print(f'{cfg}: {sum(r["passed"] for r in subset)}/{len(subset)} = {sum(r["passed"] for r in subset)/len(subset):.1%}')
    print('Saved',target)
if __name__=='__main__':
    load_dotenv();p=argparse.ArgumentParser();p.add_argument('--mock',action='store_true');args=p.parse_args();asyncio.run(main(args.mock))
