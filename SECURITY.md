# Security policy

## Project status and supported scope

VALCIER FRAMEFORGE v0.1 is a **local research and demonstration MVP**, not a publicly hosted media-generation platform. No live AI image/video provider is integrated.

The current `main` branch is the only maintained development line. There are no guaranteed security-support windows or production releases. Treat any demonstration deployment as untrusted until separately reviewed.

## Responsible disclosure

**Do not disclose an exploitable vulnerability, credentials, personal data, or attack details in a public issue.**

1. On this repository's **Security** page, use **Report a vulnerability** if private vulnerability reporting is enabled.
2. If that option is unavailable, open a **metadata-only issue** requesting a private contact channel. Include no proof of concept, exploit steps, secret values, or sensitive logs in the issue.
3. The maintainer can coordinate a private report and remediation; response times are not guaranteed for this experimental project.

For known-exposed credentials, revoke or rotate them promptly at the affected provider. Removing the value from a later commit does not make it safe.

## Security boundaries

- `FRAMEFORGE_LOCAL_DEMO=1` bypasses API authentication by design; it must never be exposed to an untrusted network.
- Keep Codespaces forwarded port **8000 private**. Never use public tunnels for the demo mode.
- Outside demo mode, `FRAMEFORGE_API_TOKEN` is a single shared token, **not** production-grade user or tenant authentication.
- Avoid real personal data, provider keys, payment details, confidential prompts, and production media in demo projects.
- SQLite, local file storage and in-process jobs are demonstration components; they have not been hardened for multi-user or Internet-facing deployment.
- Use dependency auditing, least-privilege runtime credentials, proper secret storage, authentication/authorization, rate limiting, storage policy and independent security review before considering public deployment.

## Reports most useful to maintainers

Relevant reports include unintended network exposure, access-control bypass outside the explicitly documented demo boundary, unsafe handling of API tokens, unauthorized access to project content, path traversal, dependency vulnerabilities and dangerous CI workflow permissions.

Please include affected revision, environment, impact and a minimal reproduction **through the private reporting channel only**.
