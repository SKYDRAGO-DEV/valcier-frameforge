## Problem and solution

<!-- Explain the real issue and the smallest reasonable change. -->

## Verification

- [ ] Ran `cd backend && python -m pytest -q`
- [ ] Ran `cd backend && python -m compileall -q frameforge`
- [ ] Added or updated regression tests where relevant
- [ ] Updated user-facing docs when behaviour changed

## Safety and boundaries

- [ ] No credentials, confidential prompts, SQLite databases or customer assets were committed
- [ ] Demo mode remains local-only; there is no new public authentication bypass
- [ ] New dependencies and GitHub Actions permissions were reviewed
- [ ] External provider, privacy, cost and storage implications are documented if applicable

## Compatibility / release notes

<!-- Explain any breaking change or write "None". -->
