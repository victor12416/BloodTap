"""Bounded core pacing study: automated 4-tap/s play, decisions every 5s."""
import argparse
import json
from pathlib import Path
import random
import tempfile
import time
from alpha.game import Game, alpha_new_fragments
import simulator as sim


class StudyGame(Game):
    def save(self):
        self.last_saved=self.clock()
        self.state.purchase_log=self.state.purchase_log[-100:]


def profile(seed,policy,seconds=3600,cps=4,until_bundle=False):
    elapsed=[0.0]
    with tempfile.TemporaryDirectory() as folder:
        game=StudyGame(Path(folder)/'unused.json',random.Random(seed),clock=lambda:elapsed[0],wall=lambda:elapsed[0])
        s=game.state;checkpoints=[];first_producer=None;useful_bundle=None;spent=0.0
        for t in range(5,seconds+1,5):
            elapsed[0]=float(t);game.advance();sim.click(s,cps*5)
            if game.omen_until:game.action({'action':'omen'})
            for _ in range(5000):
                options=sim.purchase_options(s,cps)
                if policy=='reserve':options=[o for o in options if s.bank-o[2]>=sim.omen_bank_reserve(s)]
                if policy=='adaptive':options=[o for o in options if s.bank-o[2]>=sim.adaptive_required_reserve(s,o[0])]
                options=[o for o in options if o[1][0]!='producer' or s.owned[o[1][1]]<1000]
                if not options:break
                _,choice,cost=max(options,key=lambda o:o[0])
                if not sim._execute_choice(s,choice,cost):raise RuntimeError('Study purchase failed')
                spent+=cost
            else:raise RuntimeError('Study policy did not stabilize')
            if first_producer is None and sum(s.owned):first_producer=t
            if useful_bundle is None and alpha_new_fragments(s)>=2:useful_bundle=t
            reached=until_bundle and useful_bundle is not None
            if t in (1800,3600,seconds) or reached:
                checkpoints.append({'seconds':t,'earned':s.run_earned,'bank':s.bank,'raw_eps':sim.raw_eps(s),
                                    'click_value':sim.click_value(s),'owned':sum(s.owned),'achievements':len(s.achievements),
                                    'prestige':alpha_new_fragments(s),'omens_collected':s.omen_clicks})
            if seconds>3600 and t%3600==0:
                print(f'Progress: {policy} seed {seed}, {t//3600} hours, {s.run_earned:.3g} earned, {alpha_new_fragments(s)} fragments',flush=True)
            if reached:break
        # No resets, losses, or Exchange trading occur in this stage-0 core profile.
        if abs(s.bank+spent-s.run_earned)>max(1e-6,s.run_earned*1e-10):raise RuntimeError('Core income/spend ledger does not conserve')
        return {'seed':seed,'policy':policy,'cps':cps,'first_producer_seconds':first_producer,
                'first_two_fragment_bundle_seconds':useful_bundle,'checkpoints':checkpoints}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds',type=int,nargs='+',default=[1,7,42])
    parser.add_argument('--policies',nargs='+',choices=['greedy','adaptive','reserve'],default=['greedy','adaptive','reserve'])
    parser.add_argument('--seconds',type=int,default=3600)
    parser.add_argument('--until-bundle',action='store_true',help='Stop each profile once two fragments are available')
    parser.add_argument('--output',type=Path,default=Path('docs/balance/core-first-hour.json'))
    args=parser.parse_args()
    if args.seconds<=0 or args.seconds%5:parser.error('--seconds must be positive and divisible by five')
    start=time.monotonic();results=[]
    for policy in args.policies:
        for seed in args.seeds:
            row=profile(seed,policy,args.seconds,until_bundle=args.until_bundle);results.append(row)
            print(json.dumps(row),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'scope':'core preview; 4 taps/s; 5s decisions; 100% Omen catch; no advanced systems or resets',
                                      'seconds_limit':args.seconds,'until_bundle':args.until_bundle,'results':results},indent=2)+'\n',encoding='utf-8')
    print(f'Completed in {time.monotonic()-start:.1f}s; saved {args.output}',flush=True)


if __name__=='__main__':main()
