# Integrated Supply Chain — training repo

Hands-on training for the Integrated Supply Chain (ISC) solution on Cognite Data Fusion: data models, seed data, workflows, Functions, and Atlas AI agents, deployed with the Cognite Toolkit (`cdf`).

This is a **single-tenant training repo**, not a multi-tenant product. The demo data is built around one dummy client, **Energy Bridge**, so you can deploy, explore, and query real data in your own CDF project without touching a customer's real data.

## Quick start

1. Set up `.env` (not committed) with your training CDF project's credentials — see [prerequisites](./docs/isc-deployment/1-overview-and-prerequisites.md) for the full list of variables.
2. Build and deploy:

   ```bash
   cdf build
   cdf deploy --dry-run
   cdf deploy
   ```

3. Load the demo graph by running `wf_btp_energy_bridge_data` in Fusion — see [Load the seed data](./docs/isc-deployment/3-load-seed-data.md).
4. Explore it with the Atlas agents, or by browsing **Data explorer** in Fusion.

`config.test.yaml` and `config.prod.yaml` ship fully configured — there's nothing to edit in them, only env vars to set.

## Repository structure

| Path | What's there |
|---|---|
| `modules/isc/` | The Cognite Toolkit modules: schema, edges, the Asset Maintenance connect module, Atlas agents, and demo seed data — see [what's in each one](./docs/isc-deployment/1-overview-and-prerequisites.md#whats-in-modulesisc) |
| `docs/` | All documentation — deployment, architecture, and the functional (business) overview |
| `config.test.yaml`, `config.prod.yaml` | Toolkit environment configs, already set up for this repo |
| `cdf.toml` | Toolkit CLI config, including the `[modules] version` this repo targets |
| `.env.example` | Template for the env vars `cdf` needs — copy to `.env` and fill in your own values |

## Documentation

Full documentation lives in [`docs/`](./docs/README.md). Start there and follow the path for your role:

| You are… | Go to |
|---|---|
| Deploying this repo into a CDF project | [`docs/isc-deployment/`](./docs/isc-deployment/) |
| Technical, and want to understand how it's built (agents, Functions, workflows, data models) | [`docs/isc-architecture/`](./docs/isc-architecture/) |
| New to ISC and want the business/supply-chain picture, no technical background needed | [`docs/isc-functional-overview/`](./docs/isc-functional-overview/) |

## Prerequisites

- A CDF project with **Cognite Functions** activated, and the Cognite Toolkit CLI (`cdf`)
- A service principal with the standard Toolkit capabilities for data modeling, RAW, transformations, files, functions, sessions, workflows, and Agents

Full details, including the exact env vars to set, are in [overview and prerequisites](./docs/isc-deployment/1-overview-and-prerequisites.md).
