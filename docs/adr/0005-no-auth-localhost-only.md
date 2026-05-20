# ADR-0005: No Authentication; Localhost-Only Binding

- **Status:** Accepted
- **Date:** 2026-05-20

## Context

This is a single-user utility the owner runs on their own machine via
Docker. Building auth (sessions, password storage, password reset, MFA)
would dwarf the rest of the application and provide no value for the
intended deployment.

## Decision

- The app does not implement any authentication or authorization.
- The Docker container binds the port to `127.0.0.1:8000` by default
  (not `0.0.0.0`), so it is not reachable from other hosts on the
  network without explicit reconfiguration.
- No CSRF tokens (single-user, localhost — minimal attack surface), but
  the framework defaults that do exist (e.g. SameSite cookies if any
  cookies are introduced later) are kept.

## Alternatives considered

- **Basic auth or a single static password.** Slight increase in safety
  if someone shares the LAN binding, but not actually mitigating a real
  threat in the intended deployment. Adds friction.
- **OAuth / proxy auth.** Out of scope; appropriate only if exposing to
  the internet (which we explicitly are not).

## Consequences

- **Do not expose this service to the internet without putting a
  reverse proxy and auth in front of it.** Documented in README.
- Code stays much simpler. No user table, no session middleware.
- A future "expose to the internet" requirement is a new project, not a
  config flag.
