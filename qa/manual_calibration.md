# Human calibration protocol

`qa/telemetry.py` is a reproducible browser-automation regression tool. Its bot intentionally has a deterministic route and shop policy, so it must not be relabeled as a 70%-skill human measurement.

To close the human balance acceptance target (198–413 seconds), collect at least 15 fresh normal-browser runs:

1. Launch `http://127.0.0.1:8791/index.html` with no `test` or `telemetry` query string.
2. Use an empty browser profile / clear the `hiveswarm_v1` local-storage key before every run so permanent tiers do not contaminate the sample.
3. Record `window.__dbg()` at death or win: `level`, `kills`, `credits`, and `firstShopCredits`; record any browser page error.
4. Report minimum, median, and maximum run duration. Separately report first-shop-arrival rate and first-shop credits.
5. Compare the human band to the 198–413-second acceptance band. If it misses, choose and document a balance change before claiming the spawn/economy rows are complete.

The current seeded continuous-bot baseline is deliberately kept separate: 15 seeds at `?telemetry=1&telemetrySpeed=60`, min/p50/max 18.1/84.0/413.0 seconds, 3/15 first-shop arrivals at 356–363 credits, zero page errors.
