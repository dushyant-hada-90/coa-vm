---
title: "Environment variable management in create_instance.sh"
model: "composer-2.5"
updated: "2026-06-18T16:15:17.023Z"
---

## User

read create_instance.sh , ensure all env vars are imported from .env file, and also fill the .env.example

## Assistant

I'll read `create_instance.sh` and the env files to see which variables are used and what `.env.example` should list.


## Assistant

Updating the script to source `.env` and filling `.env.example` with the required variables.


## Assistant

Here’s what changed:

### `create_instance.sh`
- Loads variables from `.env` next to the script (`set -a` / `source` / `set +a` so they’re exported).
- Exits with a clear message if `.env` is missing.
- Validates that `PROJECT_ID`, `ZONE`, and `INSTANCE_NAME` are set before running `gcloud`.
- Quotes variable expansions in the `gcloud` command.

### `.env.example`
Filled with the three variables the script uses:

```
PROJECT_ID=your-company-project-id
ZONE=us-central1-a
INSTANCE_NAME=coa-inference-node
```

Your `.env` is empty right now. Copy the example and set your real values:

```bash
cp .env.example .env
```

Then edit `.env` with your GCP project ID and any other overrides you want.
