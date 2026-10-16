# Contributing to the research preview

Start with a reproducible issue or a focused pull request. State the source
revision, Python and solver versions, declared finite domain, expected status,
actual status, and a minimal input. Never attach credentials or private models.

Install the pinned dependencies and package using the README. Run:

```text
python -m unittest discover -s tests -v
python -m epv doctor
```

Record discovered, passed, failed, and skipped tests separately. Without the
pinned Carcara checker, core tests can pass with explicit skips, but V3 is
unvalidated and `python -m epv.reproduce` must still report overall `FAIL`.
For proof-related changes install the checker specified in `tools.lock.json`,
run full reproduction, and retain checker output and exact bundle hashes.

For semantic changes, add a counterexample or boundary regression and compare
exhaustive and solver-backed results. Preserve finite bounds, trusted compiler
assumptions, and negative outcomes. Do not relabel UNKNOWN, ERROR, TIMEOUT, or
missing external validation as verified. Changes to frozen scientific claims,
proof bytes, benchmark expectations, or assurance definitions need an explicit
explanation and separate review.

Keep changes on a branch. Do not alter existing release history or license terms.
The current [LICENSE](LICENSE) is restrictive; this guide grants no additional
reuse rights or implied contributor agreement.
