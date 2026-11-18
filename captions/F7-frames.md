+++
id = "F7"
order = 7
title = "Frame specialisation, and a planned claim that was false"
script = "scripts/figure_f7_frames.py"
artefact = "figures/f7-frames-v1.2.0.pdf"
category = "diagnostic"
caption = """
This figure reports that its own planned claim is false, which is why it is
here. It was designed to show the dipole standing an order of
magnitude apart from the higher multipoles under a change of frame --- the
dipole being the one multipole a boost moves at first order. It does not. The
dipole lands on each curve instead: $1.00\\times$ at every probe mode, the
frame moving the transfer by $114\\%$, $162\\%$ and $101\\%$ at $k=20$, $60$ and
$140$ with the dipole on those values to within $0.3\\%$.\\\\[2pt]
The reason is structural, and it is finding \\textbf{T-31}. Equation~(102) builds
\\emph{every} $\\ell$ from the same three coefficients $C_A$, so a frame change
that moves $C_1$ moves every multipole built on it in the same proportion. A
frame response that depended on $\\ell$ would contradict the equation's own
form, and \\texttt{test\\_102\\_cannot\\_make\\_its\\_frame\\_response\\_depend\\_on\\_the\\_multipole}
asserts that it does not. The spread \\emph{over} $\\ell$ is $1.00$, $1.06$ and
$1.03$ at $k=20$, $60$, $140$. The responses exceed $100\\%$ because~(102)'s
total is not frame-invariant (\\textbf{T-59}). Regenerated on 18 November 2026
(\\textbf{T-197}); the figure it replaced read a worst ratio of $1.25\\times$.\\\\[2pt]
A figure drawn to its plan would have been drawn wrong. The plan is kept in \\texttt{captions/FIGURE-PLAN-v1.0.0.md} and the
outcome is kept here, because a reproduction bundle whose figures only ever
confirm their captions is not measuring anything.\\\\[2pt]
Its environment is built for the $k$ grid, not for the probe modes ---
finding \\textbf{T-34}, where this figure sized its $\\eta$ grid for $k=140$ and
then integrated to $k=420$. \\texttt{check\\_k} now raises rather than
interpolating past what the grid resolves.
"""
+++
