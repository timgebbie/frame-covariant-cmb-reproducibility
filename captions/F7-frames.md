+++
id = "F7"
order = 7
title = "Frame specialisation, and a planned claim that was false"
script = "scripts/figure_f7_frames.py"
artefact = "figures/f7-frames-v1.2.0.pdf"
category = "diagnostic"
caption = """
\\textbf{This figure reports that its own planned claim is false, and that is
why it is here.} It was designed to show the dipole standing an order of
magnitude apart from the higher multipoles under a change of frame --- the
dipole being the one multipole a boost moves at first order. It does not. The
dipole lands on each curve instead: worst ratio $1.25\\times$ over the probe
set, and $1.00\\times$ at $k=20$.\\\\[2pt]
\\textbf{The reason is structural and is finding T-31.} Equation~(102) builds
\\emph{every} $\\ell$ from the same three coefficients $C_A$, so a frame change
that moves $C_1$ moves every multipole built on it in the same proportion. A
frame response that depended on $\\ell$ would contradict the equation's own
form, and \\texttt{test\\_102\\_cannot\\_make\\_its\\_frame\\_response\\_depend\\_on\\_the\\_multipole}
asserts that it does not. The spread \\emph{over} $\\ell$ does grow with $k$ ---
$1.01$, $1.14$, $8.14$ at $k=20$, $60$, $140$ --- but that is the transfer
function's $k$ dependence, not the frame's $\\ell$ dependence.\\\\[2pt]
\\textbf{A figure that had been drawn to its plan would have been drawn
wrong.} The plan is kept in \\texttt{captions/FIGURE-PLAN-v1.0.0.md} and the
outcome is kept here, because a reproduction bundle whose figures only ever
confirm their captions is not measuring anything.\\\\[2pt]
\\textbf{Its environment is built for the $k$ grid, not for the probe modes} ---
finding \\textbf{T-34}, where this figure sized its $\\eta$ grid for $k=140$ and
then integrated to $k=420$. \\texttt{check\\_k} now raises rather than
interpolating past what the grid resolves.
"""
+++
