# Invoice Generator

A small, self-hosted PDF invoice generator for single-user / small-business
use. Runs as a single Docker container, stores everything in a mounted
`./data/` directory.

**Status:** design phase — implementation not yet started.

## Quickstart (once implemented)

```sh
docker compose up --build
# then open http://127.0.0.1:8000
```

First run: open `/settings`, fill in your business profile, upload your
logo. Then create clients and invoices.

## What it does

- Generates PDF invoices numbered `INV-YYYY-MM-DD-NNNN` (sequence resets
  daily).
- Stores a logo, business address, contact info, payment instructions, and
  default footer notes so you don't re-enter them every time.
- Keeps a small client directory and saved line-item presets.
- Marks invoices as paid and auto-generates a receipt PDF
  (`RCT-YYYY-MM-DD-NNNN`).
- Localhost-only — no auth, no cloud.

## Hand-off documentation

Everything an implementing agent needs:

- **[docs/PLAN.md](docs/PLAN.md)** — full implementation plan: data model,
  routes, file layout, Docker setup, verification steps.
- **[docs/adr/](docs/adr/)** — Architecture Decision Records covering the
  stack, rendering engine, numbering scheme, immutability, storage, and
  more.

## License

See [LICENSE](LICENSE).
