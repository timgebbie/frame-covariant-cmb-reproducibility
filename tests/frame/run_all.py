#!/usr/bin/env python3
"""Run every frame check.  Exit 0 only if all pass."""
import subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
CHECKS = ['c1_identity.py', 'c2_weight.py', 'c3_byparts.py',
          'c4_rank_slot.py', 'c5_monopole.py', 'c6_thomson.py', 'c7_kappa_ledger.py',
          'c8_rank0_partner.py', 'c9_byparts_admissibility.py']
fails = []
for c in CHECKS:
    print(f'\n===== {c} ' + '='*(60-len(c)))
    r = subprocess.run([sys.executable, '-I', str(HERE/c)], cwd=HERE)
    if r.returncode: fails.append(c)
print('\n' + '='*68)
print('FRAME CHECKS FAILED: ' + ', '.join(fails) if fails
      else 'ALL FRAME CHECKS PASS')
sys.exit(1 if fails else 0)
