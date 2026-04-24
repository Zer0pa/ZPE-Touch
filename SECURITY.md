# Security Policy

## Supported Scope

This policy covers security-sensitive issues in:

- package metadata and installation surfaces
- local verification and artifact-generation commands
- repository automation and release artifacts

Scientific disagreements about the bounded touch claim surface should use the public `evidence_dispute` issue template, not the security channel.

## Reporting

Report security-sensitive issues privately to `architects@zer0pa.ai`.

If GitHub private vulnerability reporting is enabled for this repository, that route is also acceptable. If no private route is available, open a minimal public issue that requests a private follow-up and do not include exploit details, secrets, or live payloads in the public thread.

Include:

- the affected file, command, or interface
- exact reproduction steps if available
- observed behavior and expected behavior
- impact assessment and any relevant logs or artifact paths

## Response Targets

- acknowledgement within 5 business days
- initial triage status within 10 business days
- remediation and disclosure timing agreed post-triage based on severity and reproducibility
