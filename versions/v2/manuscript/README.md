# Alternative proofs of Hohn's divisibility conjectures after Kontorovich and Stong

Haobo Ma (ChronoAI Pte Ltd, Singapore), then Wenlin Zhang (National
University of Singapore; ChronoAI Pte Ltd, Singapore). License: CC BY 4.0.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, run `pdflatex note.tex` twice. The bibliography is embedded;
BibTeX and external figures are unnecessary.

## Exact arithmetic

Python 3.10 or later, with its standard library, suffices:

```sh
python3 verify.py --data data/b390148.txt --bound 60 --output verification.json
```

The expected counts are 1128 primitive sphere quadruples, 5320
prime/quadruple pairs, 8040 positive prime-power thresholds, and 19 rows
with first radius at most 60 from 302620 triples. The repeated-sphere
parametrization gives 1254 quadruples for parameters 1 through 200 and
classifies all repetitions in the table. The circle parametrization is
checked on 3043 coprime pairs `1<=u<v<=100`, and its three families on
175 examples. Exhaustive containing-row checks establish the listed
unique occurrences of 1, 4, and 36. A390583's second-family expression
at `k=3` has reciprocal-equation residual `-4/315`; its corrected
sequence index `(k+1)/2` gives `(3,5,120,120)`.

Additional finite checks cover 1809 inert-prime residue pairs and the
curvature identity on 4096 tuples. The input is Charles L. Hohn's table,
https://oeis.org/A390148/b390148.txt, SHA-256
`50f1f6a5f9598aa3997b7fcd1f585a9576400aaffaaef2330505de5a1fd46b20`.
`MANIFEST.json` records exact source member sizes and SHA-256 digests.

## Mathematical coverage

Theorem 1 gives the all-prime threshold conclusion and exact 3-adic and
inert-prime valuation patterns. The text explicitly translates the earlier
results of Kontorovich (2012, Lemma 2.11), Stong (January 2015, p. 76), and
Northshield (March 2015, Corollary 4.6). McGonagle and Northshield's 2014
article already states the norm conclusion in its Section 6 sketch.
These results concern equivalent
arithmetic variables, not the later OEIS entry; no priority is claimed.

Written corollaries establish the gcd correction, enumeration bounds,
finite membership procedure, infinite-rational-chain obstruction, exact
repeated-sphere count, repeated-circle parametrization and corrected
circle families. The coverage table separates these from frequency,
gap-growth, non-enumerative construction and finite-chain questions.

The pinned Lean declaration `SplitPrimeSphereRadii.result` proves the
split-prime threshold statement under the positive common-primitive
coefficient-three hypotheses:
https://github.com/the-omega-institute/trureturing/blob/bed437cb2aa5a2d3570eb2241767ad6de36d77cc/D5/S3/Arith/Descartes/SplitPrimeSphereRadii.lean

The pinned declaration `PrimitiveSphereRadii.primitive_sphere_radii_v3`
proves the 3-adic pattern under the same hypotheses:
https://github.com/the-omega-institute/trureturing/blob/bed437cb2aa5a2d3570eb2241767ad6de36d77cc/D5/S3/Arith/Descartes/PrimitiveSphereRadii.lean

The extensions and corollaries have written proofs in `note.tex` and
`note.pdf`. The finite checks certify the specified ranges, not the
unbounded theorems. The additional mathematical coverage is stated in
the note's source-by-source table.
