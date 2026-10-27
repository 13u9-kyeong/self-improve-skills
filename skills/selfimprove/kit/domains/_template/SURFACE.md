# The denominator — <domain>

## Why "every unit of raw material" does not work here

<The sizing argument. What the raw material is, how big, and why a sample is not a
denominator.>

## The denominator

```
every <unit of input the work receives, or that the environment can change>
  ×  every <thing that must not go wrong>
```

**Left side — how it is enumerated:** <the declaration it comes from: a table, a schema, a
taxonomy, a state diagram, a registration call>

**Right side — how it is enumerated:** <same>

**Complete when:** every unit has a *disposition* — examined and cleared with a reason,
examined and filed, or explicitly deferred with the reason recorded. Not "looked at".

## The give-up bucket

Every mechanical analysis fails somewhere: <the ways it fails in this domain>.

These are **in** the denominator, as their own bucket, with their own completion gate. A
give-up recorded as a clear is indistinguishable downstream from a unit someone examined.

## Reachability / applicability record

Per unit, before any lens pass runs:

```
actor          <the privilege or position that can reach it>
precondition   <what must already be true>
default?       <true in a default configuration, or not>
```

`default?` decides scope and is the field most often left implicit. Build it from the
deployed/observed configuration, never from documentation.

## surface.json

```json
{"denominator": "<name>",
 "units": [
   {"id": "U-001", "kind": "<kind>", "where": "<locator>",
    "actor": "<>", "precondition": "<>", "default": true,
    "resolved_by": "<the declaration this was enumerated from>"},
   {"id": "G-001", "kind": "unresolved", "where": "<locator>",
    "why": "<what the analysis could not do>", "tool": "<which>"}
 ],
 "tool_gaveup_count": 0}
```

## The completion gate

```
<name>_gate.py --surface surface.json --dispositions dispositions.json

0  every unit has a disposition
1  units without one -> named, with counts per bucket
2  surface unreadable, or the denominator is EMPTY
```

An empty denominator exits **2**, never 0.
