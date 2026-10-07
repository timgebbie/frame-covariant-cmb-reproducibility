# The almost-EGS bounds: what v2.0.0 computes, and why the model matters

**Forward-looking. Nothing here is computed at v1.0.0, and the table below
carries no derived bound — only the observational inputs and the structure the
computation will fill.** Recorded now because the scope question it raises is a
v1.0.0 scope question: *which model the bounds are stated for*.

---

## What the theorem says, and why this bundle is the right place to apply it

The Ehlers–Geren–Sachs theorem states that if all fundamental observers in an
expanding dust universe measure an **exactly** isotropic CMB, the spacetime is
exactly Friedmann–Lemaître–Robertson–Walker. The **almost-EGS** theorem relaxes
"exactly" to "almost": Stoeger, Maartens & Ellis, *Ap. J.* **443**, 1 (1995), and
Maartens, Ellis & Stoeger thereafter, bound the kinematic and Weyl quantities —
$\sigma_{ab}$, $\omega_{ab}$, $\dot u_a$, $E_{ab}$, $H_{ab}$ — in terms of bounds
on the CMB multipoles $\tau_{A_\ell}$.

**The bounds are stated in exactly the variables this bundle computes.** The
almost-EGS argument is a $1+3$ covariant argument and its inputs are covariant
multipoles, not mode coefficients — the distinction *Annals II* insists on and
every released figure here respects. A gauge-fixed Boltzmann code cannot supply
them without a translation; this one supplies them directly.

That is why the bounds belong in this project rather than beside it, and it is
also why they are **v2.0.0** work: they are a *calibration* of the formalism
against data, which is precisely what v2.0.0 is for (decision S3).

---

## The table v2.0.0 fills

| Mission | Epoch | $\ell$ reach | Temperature anisotropy | Almost-EGS bound, standard CDM | Almost-EGS bound, $\Lambda$CDM |
|---|---|---|---|---|---|
| **COBE**-DMR | 1992 | $\ell\lesssim20$ | $\Delta T/T\sim10^{-5}$ at $10^\circ$ | **the original** — to be recomputed here | **not in the original** |
| **WMAP** | 2003–2013 | $\ell\lesssim1000$ | — | pending | pending |
| **Planck** | 2013–2018 | $\ell\lesssim2500$ | — | pending | pending |

**Every cell marked *pending* is pending.** No number is written here that has
not been computed by this bundle, and the observational columns are left for the
mission papers to fill at v2.0.0 rather than quoted from memory now. The rule
that equation numbers are resolved from the source applies to data values too.

---

## The qualification, which is the point of recording this early

**The original almost-EGS bounds were derived for a CDM model, not for
$\Lambda$CDM.** The PI's recollection is the reason this file exists, and it is
not a detail:

1. **The bound depends on the background.** The almost-EGS argument converts
   multipole limits into limits on $\sigma/H$ and its relatives using the
   background expansion history. $\Lambda$ changes $H(z)$ at low redshift, so a
   bound derived on an Einstein–de Sitter background does not transfer.

2. **$\Lambda$ adds a source the original did not have.** The late integrated
   Sachs–Wolfe effect contributes to precisely the low-$\ell$ multipoles the COBE
   bounds rest on. In standard CDM it is absent — $\Phi$ is constant, as this
   bundle's own growth factor reproduces to six figures. In $\Lambda$CDM it is
   not: $\Phi$ decays to $0.779$ of its early value by today. **A low-$\ell$
   multipole limit therefore constrains a different combination of quantities in
   the two models**, and a bound quoted for one is not a bound for the other.

3. **So the table carries both columns, and the CDM column is the one with a
   published precedent.** The $\Lambda$CDM column is new work.

---

## Beyond v2.0.0: the higher-order correction

The almost-EGS bounds as published are **first order** in the anisotropy
parameter. The natural extension, and the one this project is uniquely placed to
make, is the **next order** — because v1.5.0 supplies exactly the
$O(\varepsilon^2\ell)$ couplings that a second-order almost-EGS argument would
need, and no external code carries them.

**Stated as a direction, not a plan.** It sits beyond v2.0.0, it is gated on
v1.5.0 landing, and the correction's sign and magnitude are unknown until the
calculation is done. It is recorded here so that the v2.0.0 table is built in a
shape that can take a second column of corrections later, rather than being
rebuilt for it.

---

## What this does *not* license at v1.0.0

No bound, no data comparison, no mission paper cited as evidence. v1.0.0 is an
analytical reproducibility release and this file changes none of that. It is a
scope note with a table skeleton, and the skeleton is here so that the shape of
the v2.0.0 deliverable is agreed before anyone computes into it.
