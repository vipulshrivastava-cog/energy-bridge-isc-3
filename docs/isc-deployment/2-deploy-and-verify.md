# Build, deploy, and verify

*Build and deploy this repo's ISC modules, then check Fusion.*

**Before you start:** [Overview and prerequisites](./1-overview-and-prerequisites.md) is done — `.env` is set, and `config.test.yaml`/`config.prod.yaml` need no edits.

Run every command from this repo's root — not from a folder whose parent has another `.env`. Toolkit searches parent folders for one, and can pick up the wrong project.

## 1. Build

```text
cdf build --config-yaml config.test.yaml
```

## 2. Dry run

```text
cdf deploy --dry-run
```

Check the output:

- Check that the dry run plans all six ISC modules, not a subset.

If either is wrong, stop and recheck `selected` and the config — don't proceed to a real deploy.

## 3. Deploy

```text
cdf deploy
```

For prod:

```text
cdf build -e prod
cdf deploy --dry-run -e prod
cdf deploy -e prod
```

## 4. Check Fusion

Counts below are for this release of the training repo — if they don't match, re-check `selected` and the config before assuming something is broken.

| Resource | Expected |
|---|---|
| Spaces | 9 |
| Data models | 8 (5 built domain models, `AssetMaintenance`, `isc_typed_model`, `IscPlatform`) |
| Transformations | 32 |
| Functions | 1 (`fn_btp_hierarchy`), **Ready** (this can take a few minutes after the deploy ends) |
| Workflows | 2 — `wf_btp_hierarchy_path` and the demo-only `wf_btp_energy_bridge_data` (see [Functions and workflows](../isc-architecture/functions-and-workflows.md)) |
| Workflow triggers | 3 created, none skipped — one each for `BusinessUnits`, `GeoLocations`, `StorageLocations` |
| Atlas | 3 agents (`Integrated Supply Chain (Main)` and its `-sandbox-only`/`-query-only` variants), 3 Skills (`isc-model`, `isc-query`, `isc-sandbox`) |
| Location filter | `loc_energy_bridge_supply_chain` |

In Fusion: **Functions** for `fn_btp_hierarchy` Ready; **Workflows** for trigger status; **Atlas** for the agent list.

### Check by module

| Module | What to confirm |
|---|---|
| `isc_core` | Schema spaces exist. `fn_btp_hierarchy` is Ready. 3 hierarchy-path triggers are created. |
| `isc_atlas_agents` | 3 agents are listed in Atlas. No Functions to check — the agents query the graph directly. |
| `isc_connect_maintenance` | `FunctionalAsset`, `WorkOrder`, and `WorkOrderComponent` views exist — this domain has a real model, not just a placeholder. |
| `isc_seed_data_ingestion` (demo only) | `wf_btp_energy_bridge_data` is listed in Workflows, with the seed RAW tables and transformations. |

## You're done when

- `cdf deploy` finished without errors.
- `fn_btp_hierarchy` is **Ready**.
- The 3 workflow triggers are **created**, not skipped.
- The 3 Atlas agents are listed in Atlas.
- The seed workflow has completed ([Load the seed data](./3-load-seed-data.md)) — or was deliberately skipped.

## If it fails

| Symptom | Cause | Fix |
|---|---|---|
| "Unknown resource kind" on build | `[alpha_flags]` missing from `cdf.toml` (`agents = true`, `agent-skills = true`) | Add the block to `cdf.toml`. |
| The hierarchy trigger is skipped, or fails with `AADSTS700016` | `HIERARCHY_PATH_TRIGGER_CLIENT_ID` is unset | Set it in `.env` ([Overview and prerequisites](./1-overview-and-prerequisites.md)). |
| `fn_btp_hierarchy` is not Ready after about 5 minutes | Functions not activated, or a build error | Check activation, then open the Function's logs. |
| Dry run shows unexpected deletions | `selected` was changed from the shipped list | Restore the shipped `selected` list and rerun. |

## What's next

Wait until `fn_btp_hierarchy` shows **Ready** before you run the seed workflow — starting it earlier is the most common mistake at this step.

- [Load the seed data](./3-load-seed-data.md)
