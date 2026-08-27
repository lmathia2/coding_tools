# Mapping a behavior specification to a product

Before the pilot document, make four stable decisions.

## 1. Unit of interaction

Choose the smallest user action with a beginning, an optional extended middle, and an end. Name its phases in product language.

| Product shape | Example unit | Example lifecycle |
|---|---|---|
| Form/web workflow | editing or submitting a form | arrive → unchanged → dirty → submitting → resolved |
| Canvas/mobile/native UI | gesture or mode-driven action | begin → short completion → active manipulation → commit/cancel |
| CLI | command invocation | parse → reject/exit early → run → emit progress → finish |
| Chat/agent product | one turn | compose → local rejection → accepted → streaming/tool work → complete/stop |
| Background job/API workflow | one request/job | accepted → validated → running → partial/retrying → committed/failed |

## 2. Variant axis

List conditions that change the same interaction:

- role, permission, ownership, or tenant;
- selected mode or tool;
- flags, environment, configuration, or feature gate;
- current record/resource state;
- device/input method;
- online/offline or healthy/degraded dependency state.

Use the same variant rows in every feature document where they apply.

## 3. Interrupt and failure families

Derive a fixed list from these families:

1. explicit user abort;
2. user starts another action or leaves the surface;
3. environment or dependency failure;
4. target changes concurrently or becomes invalid;
5. input channel/session/process disappears;
6. timeout, retry, or duplicate delivery;
7. product-specific lifecycle transition.

Keep the order stable across documents. Fill every relevant cell, including `No observable effect`.

## 4. Cross-cutting concerns

Choose an ordered set that applies across features, such as:

- identity, authorization, and ownership;
- history, undo, audit, or event log;
- persistence and synchronization;
- offline/reconnection;
- validation and data integrity;
- notifications and external side effects;
- configuration and feature flags;
- accessibility and input methods;
- observability and support/recovery;
- compatibility, migration, and rollback.

Foundation documents own shared definitions and limits. Feature documents link to them instead of repeating them.
