#!/usr/bin/env python3
"""C2 -- the rank-2 sector enters at k^-2, and its boundary pair is in S and S',
never S''.   Audit result 1 (weight half).

    int S j_l'' deta = (1/k^2) int S'' j_l - (1/k)[S j_l'] - (1/k^2)[S' j_l]
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = 'The rank-2 weight'
AUDIT_PROSE = "The rank-2 sector enters at $k^{-2}$, and the boundary pair left by two integrations by parts is in $S$ and $S'$ — **never** $S''$."
import numpy as np
from _common import finish, j, jp, jpp, report
from scipy.integrate import quad

E0, TOL = 1.0, 1e-6
CASES = {'C2 = -eta/3  (S\'\'=0, the EdS shear potential)':
         (lambda e: -e/3.0, lambda e: -1.0/3.0, lambda e: 0.0),
         'S = sin(3e)+e^2  (S\'\' nonzero)':
         (lambda e: np.sin(3*e)+e**2, lambda e: 3*np.cos(3*e)+2*e,
          lambda e: -9*np.sin(3*e)+2.0)}
worst = 0.0
for label, (S, Sp, Spp) in CASES.items():
    for l in (2, 3, 5, 10, 40):
        for k in (1.0, 7.5, 50.0, 300.0):
            lhs = quad(lambda e: S(e)*jpp(l, k*(E0-e)), 0, E0, limit=400)[0]
            rhs = (quad(lambda e: Spp(e)*j(l, k*(E0-e)), 0, E0, limit=400)[0]/k**2
                   - (S(E0)*jp(l, 0.0) - S(0.0)*jp(l, k*E0))/k
                   - (Sp(E0)*j(l, 0.0) - Sp(0.0)*j(l, k*E0))/k**2)
            worst = max(worst, abs(lhs-rhs)/max(abs(lhs), 1e-30))
print(f'  worst relative discrepancy over 40 (l,k) pairs: {worst:.3e}')
report('C2   k^-2 weight, boundary pair in S and S\'', worst < TOL, f'worst {worst:.1e}')
finish({'worst_rel': worst, 'n_pairs': 40})
