# EPL 0.1 Specification

EPL 0.1 is a closed, JSON-syntax language for two-agent, one-item, deterministic direct mechanisms over inclusive bounded integer domains. JSON was chosen for a standardized grammar, duplicate-key rejection, and absence of implicit YAML typing.

Required top-level fields are `schema`, `protocol`, `agents`, `types`, `reports`, `resource`, `allocation`, `payments`, `utility`, `feasibility`, `outside_option`, and `assumptions`. `verify` is optional and does not affect mechanism identity.

Supported allocation rules are `highest_report`, `all_agents`, and `agent_zero`. Supported payments are `second_highest`, `own_report`, `winner_subsidy_one`, and `zero`. Positive transfer means money paid by an agent to the mechanism. Utility is only `quasi_linear_private_value`. Feasibility is only `single_item_capacity` with one indivisible item. `highest_report` requires `lowest_id` tie-breaking.

Unknown fields, floats, unsupported rules, ambiguous signs, mismatched type/report domains, non-two-agent elaboration, and unrecognized assumptions fail closed. EPL contains no execution, extension, import, or host-language escape facility.

