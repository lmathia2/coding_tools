# Verification protocol

## Purpose

Check documented claims against executable tests and the running product. Record what was actually exercised and what remains unverified.

## Environment

- source commit/build: `{commit}`
- runtime command/URL/account: `{details}`
- device/browser/OS/role/configuration: `{details}`
- external services/fixtures: `{details}`
- cleanup/reset procedure: `{details}`

## Result values

- `PASS` — observed result matches the claim.
- `FAIL` — observed result contradicts the claim.
- `BLOCKED` — required environment, device, credential, fixture, or preceding state is unavailable.
- `NOT RUN` — planned but not executed.

## Priority

- `P1` — core contract, shared foundation, data/safety risk, or suspected defect.
- `P2` — ordinary user-visible behavior.
- `P3` — presentation, exact timing, or low-impact detail.

## Checklist template

| ID | Priority | Claim/document link | Setup | Steps | Expected | Actual/evidence | Result |
|---|---|---|---|---|---|---|---|
| `{AREA}-01` | P1 | [`Feature`](../features/example.md#normal-flow) | {setup} | 1. {step}<br>2. {step} | {observable result} | {test/log/screenshot/observation} | NOT RUN |

Use stable IDs. Never silently reuse an ID for a different claim.

## Running a pass

1. Confirm source commit/build and environment.
2. Run existing automated tests first and record exact commands.
3. Run targeted probes for uncovered state/error paths.
4. Exercise visual/device/human-perception claims using the actual surface.
5. Record actual results and evidence.
6. Link every failure to an existing or new triage item.
7. Mark a document verified only when required items pass or have explicit triage decisions.

## Automation boundaries

Automated tests may establish output, state, persistence, exit codes, error behavior, and integration wiring. They do not establish visual clarity, perceived timing, keyboard/screen-reader usability, touch/pen feel, or multi-device behavior unless those environments were actually used.
