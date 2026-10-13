# The cosmological parameter set — source, column and status

**Finding T-22 recorded that this bundle was already half-Planck and said so
nowhere.** `omega_b_h2 = 0.0224` appears as a bare default in eight places and
`omega_gamma_h2 = 2.47e-5` beside it, both uncited, inside a background of round
numbers with no radiation. This file is the citation those constants never had,
and the stamp for the parameter set v1.2.0 adopts.

## The source

> Planck Collaboration, **"*Planck* 2018 results. VI. Cosmological parameters"**,
> *Astronomy & Astrophysics* **641**, A6 (2020).
> DOI [10.1051/0004-6361/201833910](https://doi.org/10.1051/0004-6361/201833910).
> Received 20 July 2018; accepted 20 March 2020.

**The column is the paper's own, not a choice made here.** Table 2's notes read:
*"Our baseline results are based on* Planck *TT,TE,EE+lowE+lensing (also given in
Table 1)."* That settles a question this bundle would otherwise have had to
adjudicate — TT+lowE and TT,TE,EE+lowE+lensing differ, and "Planck" is not a
specification.

## Table 2, TT,TE,EE+lowE+lensing, 68% limits

Sampled parameters, the top group of six:

| | value |
|---|---|
| $\Omega_bh^2$ | $0.02237\pm0.00015$ |
| $\Omega_ch^2$ | $0.1200\pm0.0012$ |
| $100\theta_{\rm MC}$ | $1.04092\pm0.00031$ |
| $\tau$ | $0.0544\pm0.0073$ |
| $\ln(10^{10}A_s)$ | $3.044\pm0.014$ |
| $n_s$ | $0.9649\pm0.0042$ |

Derived, and these are the ones this bundle checks itself against:

| | value |
|---|---|
| $H_0$ | $67.36\pm0.54$ km s$^{-1}$Mpc$^{-1}$ |
| $\Omega_\Lambda$ | $0.6847\pm0.0073$ |
| $\Omega_m$ | $0.3153\pm0.0073$ |
| $z_*$ | $1089.92\pm0.25$ |
| $r_*$ | $144.43\pm0.26$ Mpc |
| $100\theta_*$ | $1.04110\pm0.00031$ |
| $k_D$ | $0.14087\pm0.00030$ Mpc$^{-1}$ |
| $z_{\rm eq}$ | $3402\pm26$ |
| Age | $13.797\pm0.023$ Gyr |

Derived from those, dimensionless and therefore directly comparable to this
bundle, which works in $H_0=1$ units:

$$\chi_*=\frac{r_*}{\theta_*}=13873\ \text{Mpc}=3.1171\,c/H_0,\qquad
\ell_A=\frac{\pi}{\theta_*}=301.8,\qquad
\ell_D=k_D\chi_*=1954.3$$

## What this bundle already gets right, measured

Round-number $\Lambda$CDM — $\Omega_m=0.3$, $\Omega_\Lambda=0.7$,
$\Omega_r=0$ — against the above:

| | this bundle | Planck | |
|---|---|---|---|
| $\Delta\eta_*$ | $3.1955\,c/H_0$ | $3.1171\,c/H_0$ | **+2.5%** |
| $\ell_D$, $R$ included | **1985** | 1954 | **+1.6%** |
| $\ell_D$, $R$ passed as zeros (**T-21**, as the code calls it) | 1783 | 1954 | $-8.8\%$ |

**The conformal geometry is good to 2.5% at round-number parameters**, which is
why the $\ell=k\Delta\eta$ comparisons in this record are meaningful at all.

## Two constants, now cited

| | value in the code | source |
|---|---|---|
| `omega_b_h2` | 0.0224 | **Planck 2018 VI abstract**, $\Omega_bh^2=0.0224\pm0.0001$. Table 2's baseline column gives $0.02237\pm0.00015$ |
| `omega_gamma_h2` | 2.47e-5 | the photon density at $T_0=2.7255$ K, the value Planck 2018 VI adopts (its footnote 14, citing Fixsen 2009) |

Neither was cited before. Both are now, and `tables/parameters` is where they
belong at v1.2.0.

## Status

**Not yet adopted as the baseline.** The round-number $\Lambda$CDM remains what
every released v1.0.0 and v1.1.0 figure used; a stamped Planck set is proposed
for v1.2.0 **beside** it, not instead of it — decision **S12**'s rule applied to
a cosmology, and the same reason Saha is kept beside Peebles.

**`CDM_MODEL` does not change.** It is *Annals II* §8.3.2's own model — flat,
matter dominated, $h=0.5$, $\Omega_B=0.05$ — and changing it stops reproducing
the paper. The faithful model and the realistic one are different objects and
this bundle carries both.

**No empirical data enter.** A parameter point is not data: nothing here is
fitted, no likelihood is evaluated, and `CITATION.cff`'s *"Analytical release;
no empirical data are required"* survives. The numbers above are a published
parameter set, cited, used as a baseline — exactly as $\Omega_m=0.3$ was, with
the difference that this one has a source.
