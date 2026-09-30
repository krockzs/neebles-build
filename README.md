# N.E.E.B.L.E.S. BUILD

N.E.E.B.L.E.S. BUILD is the materialization layer used to compose the N.E.E.B.L.E.S. OS image.

It turns certified project inputs into filesystem state consumed by the live-build process.

## Responsibilities

- live-build configuration
- base package selection
- Calamares build integration
- materialized platform authority
- certified Boss and Calamares runtime corpora
- shared module runtime territory
- opaque materialization of domestic construction declarations
- independent recovery environment
- image-side filesystem composition

## Platform authority

Canonical platform authority belongs to N.E.E.B.L.E.S. OS.

BUILD carries its materialized copy below:

```text
config/includes.chroot/usr/lib/neebles/platform/
```

The OS-defined `neebles.domestic_workspace` authority is synchronized into the image together with the canonical AuthoritySupply.

BUILD materializes authority. It does not become the semantic owner of platform authority.

## Boss corpus

N.E.E.B.L.E.S. CUSTOM owns the certified domestic Boss runtime corpus.

BUILD carries the image-side materialization required by the OS build.

## Shared module territory

BUILD owns the image-side filesystem territory used by domestic module material:

```text
/opt/neebles-build/modules
/opt/neebles-build/modules/packages
/opt/neebles-build/modules/rootfs
```

The current directory contract is:

```text
/opt/neebles-build/modules           root:root 0755
/opt/neebles-build/modules/packages  root:root 0775
/opt/neebles-build/modules/rootfs    root:root 0755
```

This is a shared pool.

BUILD does not create a separate physical package store for every module and does not infer module technology from material placed there.

CUSTOM certifies material file metadata and integrity; BUILD governs the image-side territory.

## Domestic construction declarations

Canonical construction declarations belong to N.E.E.B.L.E.S. CUSTOM.

BUILD materializes their image-side copy under:

```text
config/includes.chroot/usr/lib/neebles/domestic/construction/
```

Materialization is performed explicitly before live-build using:

```text
scripts/sync-neebles-custom-construction.py
```

BUILD transports declaration files opaquely.

It does not interpret construction semantics, module technology, compiler identity or package-manager identity.

The installed declaration territory follows:

```text
directory     root:root 0755
declarations  root:root 0644
```

An empty CUSTOM construction namespace is valid.

## Recovery

BUILD owns the independent `neebles-check` recovery environment.

Canonical recovery source lives below:

```text
config/includes.chroot/usr/lib/neebles/neebles-check/
```

Boss normal startup does not depend on invoking the recovery engine.

### Module certification

`neebles-check` now includes a dynamic module mode:

```text
neebles-check --module <module_id>
```

Modules are not a third static checker component.

The checker resolves dynamic authority from CUSTOM:

```text
runtime/manifests/modules/<module_id>.packages.tsv
runtime/manifests/modules/<module_id>.manifest.json
```

The package selector and integrity manifest are fetched from the same remote revision/branch.

The checker verifies:

- safe dynamic module identity
- exact required DEB membership
- TSV SHA256 vs integrity-manifest SHA256 agreement
- required material type
- mode
- size
- SHA256
- symlink target
- missing required material
- changed required material

The observed shared pool is fixed to:

```text
/opt/neebles-build/modules
```

The privileged helper cannot accept a caller-selected module root.

Only paths required by the requested module are inventoried. Unrelated shared material is ignored.

A module cannot claim ownership of the shared `packages` or `rootfs` roots themselves.

Path traversal, absolute selected paths and symlink-ancestor escape are rejected.

## Point 7 boundary

Point 7 preserves the ownership split:

```text
CUSTOM  -> certified material, membership, integrity, construction semantics
OS      -> platform authority semantics
BUILD   -> image-side materialization and independent recovery
Boss    -> generic governed consumption and execution
```

BUILD does not teach Boss module technology and does not duplicate Lifecycle, Registry or AuthoritySupply semantics.

Generated build products, caches and temporary workspaces are not canonical source.
