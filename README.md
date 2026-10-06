# N.E.E.B.L.E.S. BUILD

**Current integration status (2026-10-06):** N.E.E.B.L.E.S. OS 2.0.0 remains the final OS version line. BUILD provides deterministic OS/image infrastructure, certified Boss/Calamares classic material, recovery and the generic module territories required by MaterialBinding schema 2 + RuntimeLease. Module Construction declarations are no longer image territory: Boss Preinstall authenticates them from the exact pinned CUSTOM v2 revision and persists them inside the module MaterialBinding. Fresh Live and installed-system acceptance remain runtime gates.

N.E.E.B.L.E.S. BUILD is the image-side materialization and recovery layer used to compose N.E.E.B.L.E.S. OS.

> **BUILD materializes. It does not become the semantic owner of OS authority, CUSTOM material, Boss governance or module technology.**

---

# Responsibilities

BUILD owns:

- live-build configuration;
- base image composition;
- image-side filesystem territory;
- image-side copies of certified Boss and Calamares classic material;
- image-side platform authority materialization;
- shared module territory creation;
- image-side permission reconstruction required by certified classic material;
- independent recovery environment;
- final ISO generation.

BUILD does not own:

- module-specific Construction declarations;
- module package membership truth;
- module integrity truth;
- module runtime-world truth;
- CUSTOM v2 / Esbirro semantics;
- platform authority semantics;
- Boss Lifecycle;
- Registry state.

---

# Source ownership map

```text
OS
    -> canonical platform authority + providers

CUSTOM classic
    -> certified Boss image material
    -> certified Calamares image material
    -> classic image-side metadata required by those corpora

CUSTOM v2 / Esbirro
    -> module package membership + integrity
    -> module source material
    -> module-specific Construction declarations
    -> module runtime worlds
    -> Essential module baseline authority

Boss
    -> governance
    -> dynamic Preinstall
    -> module materialization
    -> authenticated Construction/runtime-world binding
    -> release/bootstrap assets

BUILD
    -> deterministic image-side materialization
    -> generic territories
    -> independent recovery/checking
    -> final ISO
```

CUSTOM classic and CUSTOM v2 / Esbirro are separate architectural worlds. A rule that applies to dynamic module material must not be projected onto the certified Boss/Calamares material required by the image.

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

# Classic CUSTOM runtime metadata

Classic CUSTOM owns canonical integrity and effective installed metadata for the Boss and Calamares corpora baked into the image.

BUILD carries their image-side current manifests and applies certified runtime metadata generically.

Examples:

```text
/opt/neebles-build/boss/current_manifest.json
/opt/neebles-build/calamares/current_manifest.json
```

BUILD verifies material before applying privileged metadata.

There is no second hardcoded permission truth.

This section does not authorize BUILD to bake CUSTOM v2 / Esbirro module truth.

---

# Boss productive house

Image-side Boss material territory:

```text
/opt/neebles-build/boss
/opt/neebles-build/boss/packages
/opt/neebles-build/boss/rootfs
```

Canonical source remains CUSTOM classic.

BUILD is not the Boss compiler authority.

---

# Calamares productive house

Image-side Calamares material territory:

```text
/opt/neebles-build/calamares
/opt/neebles-build/calamares/packages
/opt/neebles-build/calamares/rootfs
```

Canonical source remains CUSTOM classic.

Boss and Calamares remain independent domestic corpora.

---

# Shared module territory

BUILD owns only the generic image-side directory contract:

```text
/opt/neebles-build/modules
/opt/neebles-build/modules/packages
/opt/neebles-build/modules/packages/essentials
/opt/neebles-build/modules/material
/opt/neebles-build/modules/runtime-leases
```

Current intended modes:

```text
modules             root:root 0755
packages            root:root 0775
packages/essentials root:root 0775
material            root:root 0755
runtime-leases      root:root 0755
```

This is the generic image-side territory required by the productive MaterialBinding + RuntimeLease architecture.

`packages/essentials/` is the dedicated physical house for the global Essential closure source packages.

`packages/` outside that subdirectory is the shared general/module package arsenal.

`material/<module-id>/` holds persistent authenticated MaterialBindings. `runtime-leases/` is the parent territory for ephemeral independent runtime leases. BUILD creates only these generic houses; Boss owns their productive semantics.

BUILD does **not** predeclare per-module package ownership.

---

## Module material is dynamic

The canonical module install flow is:

```text
CUSTOM v2 / Esbirro
    -> Essential package authority
    -> module package membership + integrity
    -> module source material
    -> Construction/runtime-world truth

Boss Preinstall
    -> ensure/reuse/download certified Essential DEBs
    -> ensure/reuse/download exact module delta DEBs
    -> supply module-specific Construction/runtime-world declarations

Boss materialization
    -> materialize required runtime material in /opt/neebles-build/modules

Lifecycle
    -> execute the module-declared flow
```

Therefore BUILD provides only generic territory and generic OS/platform authority infrastructure for modules.

A new module, package delta, Construction declaration or module runtime world must never require rebuilding the N.E.E.B.L.E.S. ISO.

---

# Module Construction boundary

BUILD owns no module Construction declaration territory.

Module-specific Construction truth remains owned by CUSTOM v2 / Esbirro.

The productive path is:

```text
exact pinned CUSTOM v2 revision
    -> Boss Preinstall
    -> validate Construction subject against module identity
    -> MaterialBinding schema 2
    -> authenticated construction.json + SHA256
    -> Lifecycle / Workspace execution
```

Construction declarations are therefore runtime material authority bound to the installed module, not static image resources.

Adding, updating or removing a module Construction declaration must never require rebuilding the N.E.E.B.L.E.S. ISO.

---
# Dynamic module runtime authority

BUILD carries the generic platform descriptor:

```text
/usr/lib/neebles/platform/authority/modules.runtime.json
```

That descriptor remains generic image infrastructure.

Its declared manifest path is not a persistent shared module runtime authority. For `modules.runtime`, Boss creates an authenticated RuntimeLease and substitutes the execution manifest with the lease-private `domestic-runtime.json` before Workspace execution.

The runtime manifest payload itself remains CUSTOM v2 / Esbirro module truth and is **not** baked into BUILD.

The Boss/bootstrap `runtime_archive` and its own `domestic-runtime.json` belong to the separate Boss classic/bootstrap world and are not part of this module rule.

---

# Required pre-build synchronization

Before a new integrated ISO:

```text
1. synchronize current OS platform authority/providers
2. synchronize current certified Boss/Calamares classic image material when required
3. verify image-side manifests and byte parity
4. verify BUILD-created generic territories and modes
5. verify recovery/checker syntax and contracts
6. only then run live-build
```

CUSTOM v2 / Esbirro module declarations, module runtime worlds and module package material are not pre-build synchronization inputs for the ISO.

A successful `lb build` against stale OS or classic Boss/Calamares image material is not a valid N.E.E.B.L.E.S. image.

---

# Recovery

BUILD owns the independent recovery environment:

```text
neebles-check
```

Normal Boss startup does not depend on recovery.

Component and module checks remain separate.

Dynamic module verification uses:

```text
neebles-check --module <module_id>
```

Global Essential module-baseline verification uses:

```text
neebles-check --modules essentials
```

Both retrieve their canonical package authority from CUSTOM v2 / Esbirro.

`--module <module_id>` verifies only the required delta/material declared for that module and ignores unrelated shared pool contents.

`--modules essentials` verifies the dedicated Essential package house exactly against `runtime/manifests/modules/essentials.packages.tsv`.

The checker is verify-only for these module scopes. It does not download, materialize or repair module material.

---

# Module checker laws

For a concrete module, the checker validates the existing module manifest/package contract, including:

- safe module identity;
- required package membership;
- TSV/manifest SHA agreement;
- declared file metadata;
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

For the Essential baseline:

```text
neebles-check --modules essentials
```

the authority is:

```text
runtime/manifests/modules/essentials.packages.tsv
```

and the observed physical house is:

```text
/opt/neebles-build/modules/packages/essentials
```

The Essentials checker validates:

- selector syntax;
- exact filename membership;
- regular-file type;
- SHA256;
- missing packages;
- extra packages;
- modified packages.

The package count is derived from the authority and is never hardcoded.

Rootfs verification is a separate concern and is not implied by `--modules essentials`.

---

# Image-side Boss and Calamares baseline

BUILD does not use prose in this README as release authority for Boss or Calamares.

The certified image-side manifests/material present in the BUILD tree are the integration truth for the ISO being cooked.

Boss bootstrap remains capable of resolving its own stable release/bootstrap contract independently.

Do not infer a CUSTOM v2 module rule from the Boss/Calamares classic material model.

---

# N.E.E.B.L.E.S. OS 2.0.0 boundary

N.E.E.B.L.E.S. OS 2.0.0 establishes the current generic image boundary:

- OS platform authority/providers are image resources;
- Boss and Calamares classic certified material may be image resources;
- generic module territories are image resources;
- module Construction declarations are not image resources and enter through authenticated MaterialBinding;
- `neebles-check` is an image recovery/checking resource;
- module-specific CUSTOM v2 / Esbirro truth is dynamic;
- adding a new module must not require rebuilding the ISO.

The 2.0.0 version is carried by the OS surfaces used by the Live and installed system.

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
    -> verify N.E.E.B.L.E.S. OS 2.0.0 identity
    -> verify Live environment
    -> verify complete AuthoritySupply
    -> verify generic module territories
       -> /opt/neebles-build/modules/packages/essentials
       -> /opt/neebles-build/modules/material
       -> /opt/neebles-build/modules/runtime-leases
    -> verify Calamares runtime
    -> verify Boss bootstrap
    -> verify installer/auth path
    -> install Test Module
       -> Boss Preinstall establishes/reuses Essential baseline
       -> Boss Preinstall establishes/reuses Test Module delta
       -> module-specific Construction/runtime-world truth is supplied dynamically
    -> run neebles-check --modules essentials
    -> run neebles-check --module test-module
    -> verify real materialization
    -> Open Test Module
    -> verify persistent runtime birth
    -> verify Module IPC registration
    -> verify UI / settings / Tray / notifications where applicable
    -> uninstall / reinstall
    -> verify shared package reuse
    -> install OS
    -> verify installed-system behavior
```

Only the real image gate closes runtime acceptance.

---

# 2.0.0 documentation state

Obsolete current-state documentation includes any claim that:

```text
BUILD bakes a concrete module Construction declaration
BUILD creates a generic static Construction declaration territory
BUILD bakes CUSTOM v2 module domestic-runtime.json
a reference module package/rootfs world is an ISO input
the old flat module package set is the current module architecture
the Essential baseline belongs to each module manifest
```

Current truth is:

```text
BUILD creates generic territories
CUSTOM classic Boss/Calamares remains a separate image-material world
CUSTOM v2 / Esbirro owns dynamic module truth
Boss Preinstall supplies dynamic module requirements
MaterialBinding schema 2 carries authenticated Construction truth
Essential packages have a dedicated shared house
neebles-check --modules essentials verifies that house
N.E.E.B.L.E.S. OS version: 2.0.0
```

---

# Final principle

BUILD must remain boring.

It should deterministically materialize certified truths from their real owners.

If BUILD starts deciding module technology, Construction meaning, platform authority semantics or Boss behavior, ownership has drifted.

---
