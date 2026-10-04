# N.E.E.B.L.E.S. BUILD

**Current integration status (2026-10-04):** image-side architecture remains valid, but the working tree must be resynchronized with the current OS authority set and CUSTOM Construction before the next ISO. Latest published Boss is 1.0.22; Boss 1.0.23 and the next integrated image are pending.

N.E.E.B.L.E.S. BUILD is the image-side materialization and recovery layer used to compose N.E.E.B.L.E.S. OS.

> **BUILD materializes. It does not become the semantic owner of OS authority, CUSTOM material, Boss governance or module technology.**

---

# Responsibilities

BUILD owns:

- live-build configuration;
- base image composition;
- image-side filesystem territory;
- image-side copies of certified Boss and Calamares material;
- image-side platform authority materialization;
- image-side Construction declaration materialization;
- shared module territory creation;
- effective permission reconstruction from CUSTOM manifests;
- independent recovery environment;
- final ISO generation.

BUILD does not own:

- Construction semantics;
- module package membership truth;
- module integrity truth;
- runtime world semantics;
- platform authority semantics;
- Boss Lifecycle;
- Registry state.

---

# Source ownership map

```text
OS
    -> canonical platform authority + providers

CUSTOM
    -> certified Boss/Calamares/module material
    -> Construction declarations
    -> manifests/worlds

Boss
    -> release assets and governance

BUILD
    -> deterministic image-side materialization
```

---

# Platform authority

Canonical source:

```text
neebles-os/platform/authority/
neebles-os/platform/bin/
```

Image-side destination:

```text
config/includes.chroot/usr/lib/neebles/platform/
```

BUILD must synchronize the **complete current OS authority set**.

Current OS authority identities include:

```text
platform.filesystem_boundary
platform.desktop_session_interface
system.dns_resolver_config
boss.modules.install_staging
boss.modules.update_staging
neebles.domestic_workspace
boss.modules.ipc
boss.runtime
modules.runtime
modules.installed_runtime
```

The sync script must not preserve an obsolete hardcoded subset.

---

## Platform file modes

Image-side contract:

```text
authority JSON descriptors  root:root 0644
platform providers          root:root 0755
```

BUILD may normalize filesystem metadata required by the image.

It must not modify source semantics or bytes.

Publication is transactional.

---

# CUSTOM runtime metadata

CUSTOM owns canonical integrity and effective installed metadata.

BUILD carries image-side current manifests and applies certified runtime metadata generically.

Examples:

```text
/opt/neebles-build/boss/current_manifest.json
/opt/neebles-build/calamares/current_manifest.json
```

BUILD verifies material before applying privileged metadata.

There is no second hardcoded permission truth.

---

# Boss productive house

Image-side Boss material territory:

```text
/opt/neebles-build/boss
/opt/neebles-build/boss/packages
/opt/neebles-build/boss/rootfs
```

Canonical source remains CUSTOM.

BUILD is not the Boss compiler authority.

---

# Calamares productive house

Image-side Calamares material territory:

```text
/opt/neebles-build/calamares
/opt/neebles-build/calamares/packages
/opt/neebles-build/calamares/rootfs
```

Canonical source remains CUSTOM.

Boss and Calamares remain independent domestic corpora.

---

# Shared module territory

BUILD owns the image-side directory contract:

```text
/opt/neebles-build/modules
/opt/neebles-build/modules/packages
/opt/neebles-build/modules/rootfs
```

Current intended modes:

```text
modules   root:root 0755
packages  root:root 0775
rootfs    root:root 0755
```

This is a shared cumulative territory.

BUILD does **not** predeclare per-module package ownership.

---

## Important: module material is not baked blindly into BUILD

The canonical module install flow is:

```text
CUSTOM
    -> package membership + material integrity + source material

Boss Preinstall
    -> verify/reuse/download exact required DEBs

Boss materialization
    -> create required runtime material in /opt/neebles-build/modules

Lifecycle
    -> execute module flow
```

Therefore BUILD should provide the territory and required authority/declaration infrastructure.

It must not duplicate the entire module package/rootfs world into the image merely because one reference module currently uses it, unless a future explicit image contract says otherwise.

---

# Domestic Construction declarations

Canonical source:

```text
neebles-custom/runtime/construction/
```

Image-side destination:

```text
config/includes.chroot/usr/lib/neebles/domestic/construction/
```

Synchronizer:

```text
scripts/sync-neebles-custom-construction.py
```

The same synchronization transaction also materializes the canonical shared module runtime manifest from neebles-custom/runtime/modules/domestic-runtime.json into config/includes.chroot/opt/neebles-build/modules/domestic-runtime.json.

The module runtime manifest remains CUSTOM-owned. BUILD validates its generic runtime contract, stages it, verifies byte parity, and publishes it into the image-side shared module territory.

BUILD copies declarations opaquely.

It does not parse or reinterpret:

- `runtime_authority`;
- `world`;
- execution mode;
- session;
- mount semantics;
- module technology.

Those semantics belong to CUSTOM/Boss contracts.

---

# Required pre-build synchronization

Before a new integrated ISO:

```text
1. synchronize current OS platform authority/providers
2. synchronize current CUSTOM Construction declarations and shared module runtime manifest
3. synchronize current certified Boss/Calamares image material when required
4. verify manifests and byte parity
5. verify BUILD-created territory and modes
6. only then run live-build
```

A successful `lb build` against stale synchronized material is not a valid N.E.E.B.L.E.S. image.

---

# Recovery

BUILD owns the independent recovery environment:

```text
neebles-check
```

Normal Boss startup does not depend on recovery.

Dynamic module verification uses:

```text
neebles-check --module <module_id>
```

The checker retrieves the module's package-membership and integrity contracts from the same CUSTOM revision.

It verifies only required module material and ignores unrelated shared pool contents.

---

# Module checker laws

The checker validates:

- safe module identity;
- exact required package membership;
- TSV/manifest SHA agreement;
- file type;
- mode;
- size;
- SHA256;
- symlink target;
- missing material;
- modified required material;
- traversal/symlink escape.

A module cannot claim the shared pool roots themselves.

The observed module root is fixed to:

```text
/opt/neebles-build/modules
```

---

# Current Boss release baseline

Latest published Boss release:

```text
1.0.22
```

Current published baseline used by the previous integration pass:

```text
Boss source commit:
21923d5117a06b315dc8bcc0eb0d414c7e0b425d

Certified CUSTOM revision:
580e5948f25cc64e44d07976699f676de7a99174

Controlled Qt world:
6.8.2
```

Those values describe **1.0.22 only**.

They must not be reused as 1.0.23 truth.

---

# Boss 1.0.23 boundary

Boss 1.0.23 is not considered ready for BUILD until:

- Test Module is committed to an immutable revision;
- Boss Registry points to that revision;
- CUSTOM Construction points to that revision;
- CUSTOM current material/worlds are committed;
- Boss release workflow pins the new exact CUSTOM revision;
- Cargo version surfaces are 1.0.23;
- release workflow/trigger/notes are 1.0.23;
- 1.0.23 release assets are published and verified.

After publication, BUILD documentation/material references can be updated to the new release assets.

---

# Why a new ISO is required

The OS platform authority set changed after the previous image.

New image-side requirements include:

```text
boss.modules.ipc
boss.runtime
modules.runtime
modules.installed_runtime
```

The platform providers also changed.

These are OS-owned physical image resources.

Therefore installing Boss 1.0.23 onto an old Live image is not sufficient for final certification.

A new integrated ISO is required.

---

# Canonical ISO build

After synchronization and certification:

```text
cd ~/NEEBLES/neebles-build
sudo lb clean --chroot
sudo lb clean --binary
sudo rm -rf .build
sudo lb config
sudo env WGET_OPTIONS="--inet4-only --timeout=30 --tries=5" lb build
```

A successful build only proves that an ISO was generated.

It does not prove runtime behavior.

---

# Fresh Live acceptance

Required final gate:

```text
boot new ISO
    -> verify Live environment
    -> verify complete AuthoritySupply
    -> verify Calamares runtime
    -> verify Boss bootstrap
    -> verify installer/auth path
    -> install Test Module
    -> verify 47-DEB Preinstall behavior
    -> verify real materialization
    -> Open Test Module
    -> verify persistent runtime birth
    -> verify Module IPC registration
    -> verify UI / settings / Tray / notifications where applicable
    -> uninstall / reinstall
    -> verify package reuse
    -> install OS
    -> verify installed-system behavior
```

Only the real image gate closes runtime acceptance.

---

# Current documentation cleanup

Historical text that says:

```text
pre-1.0.22
Boss 1.0.21 is current
1.0.22 is not published
```

is obsolete and must not remain as current-state documentation.

Current truth is:

```text
latest published Boss: 1.0.22
next Boss release: 1.0.23
next integrated ISO: pending
```

---

# Final principle

BUILD must remain boring.

It should deterministically materialize certified truths from their real owners.

If BUILD starts deciding module technology, Construction meaning, platform authority semantics or Boss behavior, ownership has drifted.
