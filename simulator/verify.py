"""Run the recovered and test-supported BloodTap simulator contract."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all',action='store_true',help='Include any preserved milestone scripts outside the declared set')
    args=parser.parse_args()
    root=Path(__file__).resolve().parent.parent
    scripts=['test_core','test_v19_fidelity','test_v20_blood_moon','test_v21_exchange_capacity','test_v22_exchange_exact','test_v23_garden_neighbors','test_v24_garden_mutations','test_v25_garden_contamination','test_v26_quiet_veil','test_v27_oaths_complete','test_v28_calendar_core']
    if args.all:
        scripts += [p.stem for p in sorted((root/'simulator/tests').glob('test_v*.py'))
                    if p.stem not in scripts and p.stem!='test_v19_integration']
    commands=[['-m','simulator.tests.'+name] for name in scripts]
    commands.append(['-m','unittest','simulator.tests.test_v19_integration',
                     'simulator.tests.test_blood_moon_boundaries','simulator.tests.test_ownership_boundaries',
                     'simulator.tests.test_exchange_boundaries','simulator.tests.test_garden_boundaries',
                     'simulator.tests.test_mutation_boundaries','simulator.tests.test_contamination_boundaries',
                     'simulator.tests.test_quiet_veil_boundaries','simulator.tests.test_oath_boundaries',
                     'simulator.tests.test_calendar_boundaries'])
    failed=0
    for command in commands:
        result=subprocess.run([sys.executable,'-B',*command],cwd=root)
        failed+=bool(result.returncode)
    if not args.all:
        print('Scope: recovered core + every preserved v0.19-v0.28 assertion. Passing does not establish the missing full Garden, Exchange, Oath, or Calendar specification.',flush=True)
    return int(failed>0)


if __name__=='__main__':sys.exit(main())
