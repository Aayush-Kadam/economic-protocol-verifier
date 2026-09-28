# M8 recovered-work audit

The interrupted M8 snapshot is preserved at commit `304384ed177e06ce673bb2f6e352a0f85a271538` on `recovery/interrupted-m8-wip`. This audit was performed from an isolated archive before selective reuse. The snapshot was not merged or cherry-picked.

| Component | Classification | Reason |
|---|---|---|
| `src/epv/cli.py`, `src/epv/__main__.py` | REUSE AFTER FIX | Thin orchestration over the M0-M7 core and six recovered workflow tests pass. Diagnostics and negative-path behavior need release review. |
| `src/epv/reproduce.py` | REUSE AFTER FIX | Exercises real V1/V2/V3, replay, synthesis, and repair paths. Output and full-mode reporting need final validation. |
| `tests/test_m8_release.py` | REUSE AFTER FIX | Exercises real CLI semantics rather than existence alone. Additional V3, fail-closed, registry, and release-byte tests are needed. |
| `property-registry.json` and registry documentation | REUSE AFTER FIX | Fourteen immutable property IDs match the M5 registry; definitions and demonstrated assurance need automated cross-checks. |
| `benchmarks/manifest.json` and benchmark documentation | REUSE AFTER FIX | Coverage is coherent, but several recorded unittest commands are not portable from the repository root and require correction. |
| Quickstart, theory, certificate, synthesis, trust, and limitations documents | REUSE AFTER FIX | Trust boundary and bounded scope are substantially correct; commands and terminology require claim-audit validation. |
| Hostile-referee audit and scripted user stories | REUSE AFTER FIX | Objections are appropriately structured and not fictional; workflows must be re-executed after CLI finalization. |
| Novelty audit, literature review, and prior-art matrix | REUSE AFTER FIX | Framing is restrained, but the snapshot broke two historical M0 tests and requires a current primary-source refresh while preserving the historical CSV contract. |
| Manuscript source | REUSE AFTER FIX | Structure and evidence are promising; every number, citation, assurance claim, and limitation requires traceability review. |
| `scripts/build_paper.py` | REUSE AFTER FIX | Deterministic local builder is usable; PDF must be rebuilt, rendered, and inspected. |
| Recovered manuscript PDF | GENERATED ARTIFACT | Not authoritative. Rebuild from the validated manuscript source after integration. |
| Release notes, package metadata, dependency/tool locks | REUSE AFTER FIX | Appropriate for a local `0.1.0` research candidate; installation claims and license wording require final audit. |
| `src/economic_protocol_verifier.egg-info/` and `tmp/pdfs/` | GENERATED ARTIFACT | Build metadata and temporary render pages are not source artifacts and remain only in the external salvage backup. |
| Web/playground | DEFER | No recovered implementation exists, and a web surface adds risk without scientific evidence. |

## Isolated recovered-snapshot result

The recovered snapshot ran 147 tests. Its six M8 CLI/reproduction tests passed, but two historical M0 tests failed because the novelty wording and `PRIOR_ART_MATRIX.csv` column contract had been replaced. This confirms that selective repair is required before integration.

## Reuse rule

Only individually reviewed files are restored onto the clean M7 `main`. Historical M0-M7 semantics, tags, and proof bytes remain unchanged. Generated artifacts are rebuilt only from validated sources.
