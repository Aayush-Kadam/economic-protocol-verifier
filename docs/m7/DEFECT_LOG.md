# M7 defect log

| ID | Severity | Component | Discovery | Impact | Fix / regression | Status |
|---|---|---|---|---|---|---|
| M7-001 | HIGH | proof validator | missing-file attack | legacy validator raised instead of returning fail-closed rejection | catch missing proof/problem; `test_missing_files_fail_closed` | resolved |
| M7-002 | HIGH | synthesis objective | malformed-prior attack | duplicate, missing, negative, or zero-total priors could corrupt or crash objective claims | exact complete positive-total prior validation; `test_malformed_priors_rejected` | resolved |
| M7-003 | HIGH | repair | out-of-class baseline | payment-only minimum could be claimed when baseline allocation was outside the preserved class | explicit allocation-membership validation; `test_repair_rejects_out_of_class_baseline` | resolved |
| M7-004 | MEDIUM | cvc5 adapter | generated singleton problem | unary `OR` crashed cvc5 adapter | direct singleton assertion; generated matching regression | resolved |
| M7-005 | MEDIUM | EPL parser | resource fuzzing | unbounded source/domain sizes exposed easy resource exhaustion | 1 MB source and 1,000-value domain limits; resource regressions | resolved |
| M7-006 | MEDIUM | proof replay | hash-seed/cold-start repeat | first cold WSL Carcara run exceeded the 30-second default and failed closed | 60-second default; explicit injected timeout remains tested | resolved |

No CRITICAL defect was found. No HIGH defect remains unresolved.
