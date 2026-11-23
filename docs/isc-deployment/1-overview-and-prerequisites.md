# Deploy Integrated Supply Chain: overview and prerequisites

*What deploying this training repo involves, and what to have ready before you start.*

**Who this is for:** trainees and instructors deploying this hands-on ISC repo into a CDF project. New to ISC? Read [what it is](../isc-functional-overview/overview.md) first — this page is about deploying it, not what it models.

## What deploying involves

This repo **is** the deployable unit — it's a self-contained Cognite Toolkit project. `config.test.yaml` and `config.prod.yaml` are already fully set up — every variable is either a pre-filled shipped value or an env-var reference, so there's nothing in those files to edit. The only thing left for you to do is set the env vars below, then build and deploy with the Toolkit CLI (`cdf`):

- [Build, deploy, and verify](./2-deploy-and-verify.md)
- [Load the seed data](./3-load-seed-data.md)

## What's in `modules/isc/`

| Module | Role |
|---|---|
| `isc_core` | The supply-chain schema (Organizational Foundation, Material Management, Sourcing & Procurement, Shipment & Delivery, Planning & Forecasting), the platform space, the location filter, and the hierarchy sync Function, workflow and triggers. |
| `isc_edges` | Edge (relationship) types for the schema above — both the fixed `isc_core_edges` and the `isc_connect_edges` layer that ties into maintenance data. |
| `isc_connect_maintenance` | Asset Maintenance: `FunctionalAsset`, `WorkOrder`, `WorkOrderComponent` — fully built and seeded with demo data in this repo. |
| `isc_atlas_agents` | The 3 Atlas agents (`integrated-supply-chain-main-agent`, `-sandbox-only`, `-query-only`) that answer supply-chain questions by querying the graph directly — no Functions attached. |
| `isc_seed_data_ingestion` (demo only) | The Energy Bridge demo graph: RAW tables, transformations, and `wf_btp_energy_bridge_data`. Seed data only — this is what makes the training repo explorable. |

All five modules are in `environment.selected` in both `config.test.yaml` and `config.prod.yaml` — there's no "optional add-on" split in this repo the way a multi-tenant product might have.

Of ISC's 7 core business domains, `isc_core` builds 5 (Organizational Foundation, Material Management, Sourcing & Procurement, Shipment & Delivery, Planning & Forecasting) — Customer Demand Fulfilment and Technical Structure aren't part of this repo. `isc_connect_maintenance` isn't one of the 7 core domains; it's the Asset Maintenance **connect layer**, where the model wires to a customer's own plant/maintenance systems. See [Data models](../isc-architecture/data-models.md#spaces) for how the domain, connect-layer, and support spaces (platform, typed model) break down.

> **Never:**
> - Commit `.env` to any repository — it holds secrets.

## What `cdf deploy` doesn't do

`cdf deploy` creates schema, the Function, and the workflows. It does **not** load data into the domain models. For the demo graph, manually run `wf_btp_energy_bridge_data` in Fusion afterward — [Load the seed data](./3-load-seed-data.md).

## Before you start

`cdf auth verify` should succeed against your training CDF project before you touch `config.<env>.yaml`.

- A CDF project with **Cognite Functions** activated — request it if it isn't already; allow up to ~2 hours.
- A service principal with the standard Toolkit capabilities for the resource kinds this repo uses: data modeling, RAW, transformations, files, functions, sessions, and workflows — plus whatever capability your CDF version requires for Agents, since `isc_atlas_agents` ships `Agent` resources.
- `.env` set up for [`client_credentials`](https://docs.cognite.com/cdf/deploy/cdf_toolkit/guides/auth#client_credentials) — the same as any Toolkit project — plus one ISC-specific variable with no fallback:

  ```text
  HIERARCHY_PATH_TRIGGER_CLIENT_ID=<entra-app-id>
  ```

  Use the same value as your main `IDP_CLIENT_ID` if your training tenant uses one Entra app. If it's unset, the hierarchy-path workflow trigger is skipped or fails at Entra with `AADSTS700016`.
- The Cognite Toolkit CLI (`cdf`), matching the `[modules] version` this repo's `cdf.toml` pins.

This repo already ships with a worked example baked in — the demo "customer" is a dummy client called **Energy Bridge** (see `btpSeedDbName: btp_energy_bridge_lng_demo` and `loc_energy_bridge_supply_chain` in `config.test.yaml`). You don't need to invent tenant values; just point `cdf_project`, `cdf_cluster`, and `idp_tenant_id` at your own training CDF project through the env vars below — `config.test.yaml`/`config.prod.yaml` already reference them.

| Value | Where it comes from |
|---|---|
| CDF project | Your training project, via `CDF_PROJECT` |
| Cluster | Your training cluster, via `CDF_CLUSTER` |
| Entra tenant ID | Your training Entra tenant GUID, via `IDP_TENANT_ID` |
| Instance space | Shipped as `sp_isc_supply_chain_instances` — no need to invent one |
| RAW database | Shipped as `btp_energy_bridge_lng_demo` — no need to invent one |

### What's already fixed in `config.<env>.yaml`

Everything below ships with the correct value already and never needs editing — it's here for reference, not as a task:

| Variable | Value |
|---|---|
| `dmVersion` | `v1.0.0` — versions every ISC data model |
| `viewVersion` | `v1.0.0` — versions every ISC view |
| `isc_OrganizationalFoundationSchemaSpace` | `sp_isc_organizational_foundation` |
| `isc_MaterialManagementSchemaSpace` | `sp_isc_material_management` |
| `isc_AssetMaintenanceSchemaSpace` | `sp_isc_asset_maintenance` |
| `isc_ShipmentDeliverySchemaSpace` | `sp_isc_shipment_delivery` |
| `isc_SourcingProcurementSchemaSpace` | `sp_isc_sourcing_procurement` |
| `isc_PlanForecastSchemaSpace` | `sp_isc_plan_forecast` |
| `isc_IscPlatformSchemaSpace` | `sp_isc_platform` |
| `isc_TypedModelSchemaSpace` | `sp_isc_solution` |
| `isc_InstanceSpace` | `sp_isc_supply_chain_instances` |
| `btpSeedDbName` | `btp_energy_bridge_lng_demo` |

`environment.selected` is also already set in both config files to all five modules under `modules/isc/` (see the module table above) — nothing to add there either, unless you deliberately want to drop `isc_seed_data_ingestion` for a no-demo-data run.

## Deploy

1. **Env** — set in `.env` (not committed): `CDF_PROJECT`, `CDF_CLUSTER`, `IDP_TENANT_ID`, the [`client_credentials`](https://docs.cognite.com/cdf/deploy/cdf_toolkit/guides/auth#client_credentials) variables, plus `HIERARCHY_PATH_TRIGGER_CLIENT_ID`.
2. **Build** — `cdf build --env <env>`, using this repo's own `config.test.yaml` / `config.prod.yaml`.
3. **Dry-run** — `cdf deploy --dry-run --env <env>`. Review the plan.
4. **Deploy** — `cdf deploy --env <env>`.
5. **Seed** (optional) — run `wf_btp_energy_bridge_data` in Fusion — see [Load the seed data](./3-load-seed-data.md).

## Check it worked

`cdf auth verify` succeeds and reports your training project and cluster.

## What's next

- [Build, deploy, and verify](./2-deploy-and-verify.md)
