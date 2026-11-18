# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 0.4.x | yes |
| 0.3.x and earlier | no |

## Reporting a vulnerability

Use GitHub's private vulnerability reporting on the repository
(**Security → Report a vulnerability**). Do not open a public issue for a
security problem.

Please include:

- the affected script or file;
- the command that triggers the problem;
- the impact (code execution, data exposure, path traversal, etc.);
- a minimal reproduction if possible.

## Scope

This repository ships analysis code, aggregate tables and synthetic sample
data. It does not contain raw CBDB records, famine event tables or person-level
links. Reports about the **data boundary** (a private table accidentally
committed) are treated as security reports and handled the same way.

## Response

We aim to acknowledge within 7 days and to publish a patched release with a
note in `CHANGELOG.md`. Please do not disclose the issue before a fix is
available.
