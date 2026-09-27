# N.E.E.B.L.E.S. BUILD

N.E.E.B.L.E.S. BUILD is the materialization layer used to compose the N.E.E.B.L.E.S. OS image.

It turns certified project inputs into filesystem state consumed by the live-build process.

## Responsibilities

- live-build configuration
- base package selection
- Calamares build integration
- materialized platform authority
- certified Boss and Calamares runtime corpora
- independent recovery environment
- image-side filesystem composition

## Platform authority

Canonical platform authority belongs to N.E.E.B.L.E.S. OS.

BUILD carries its materialized copy below:

```text
config/includes.chroot/usr/lib/neebles/platform/
```

## Boss corpus

N.E.E.B.L.E.S. CUSTOM owns the certified domestic Boss runtime corpus.

BUILD carries the image-side materialization required by the OS build.

## Recovery

BUILD owns the independent `neebles-check` recovery environment.

Canonical recovery source lives below:

```text
config/includes.chroot/usr/lib/neebles/neebles-check/
```

Generated build products, caches and temporary workspaces are not canonical source.
