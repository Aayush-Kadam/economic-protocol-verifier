# Fuzzing

The deterministic EPL campaign used 200 malformed documents across malformed/truncated JSON, wrong top-level types, missing required fields, unknown fields, null semantic sections, deep nesting, oversized source, and oversized domains. All failed closed with `EPLError`. Six valid formatting variants preserved semantic identity while changing source identity.

Core semantic generation used only valid bounded mechanisms/markets/instances. Failures are reproducible from committed seed `7001`; no nondeterministic fuzz state is required.
