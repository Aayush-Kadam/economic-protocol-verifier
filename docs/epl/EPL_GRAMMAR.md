# EPL 0.1 Grammar

Lexical and structural syntax is RFC 8259 JSON, restricted by this schema:

```text
protocol := object(
  schema = "epv-epl-0.1",
  protocol = string,
  agents = {count: positive-integer, prefix: nonempty-string} | {ids: unique-string-list},
  types = integer-domain,
  reports = integer-domain,
  resource = {kind: "single_indivisible", capacity: 1},
  allocation = {rule: allocation-rule, tie_break: tie-rule},
  payments = {rule: payment-rule, sign: "agent_pays_mechanism"},
  utility = {rule: "quasi_linear_private_value"},
  feasibility = {rule: "single_item_capacity"},
  outside_option = integer,
  assumptions = ["private_values", "quasi_linear"],
  verify? = property-list
)
integer-domain := {integer: {min: integer, max: integer}}
```

Duplicate object keys are invalid. Comments are not part of EPL 0.1.

