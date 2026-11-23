# Security policy

Report suspected vulnerabilities privately through [GitHub private vulnerability reporting](https://github.com/Chris-1337/KISS-Chris-Stack/security/advisories/new), which is enabled for this public repository. Do not create a public issue or discussion containing exploit details or secrets.

Never include passwords, access tokens, private keys, personal configuration, or unredacted logs in issues, discussions, or pull requests. For suspected credential exposure, preserve minimal redacted evidence and have the authorized credential owner promptly revoke or rotate the affected credential, then verify recovery. Deleting a file or rewriting Git history does not invalidate the credential. Agents need actual authorization for credential changes and outbound reports; this reporting policy grants neither. The existing confirmed-expired managed SonarQube token preflight is separate from exposure response and does not authorize rotating other credentials. See [operations and incident response](docs/OPERATIONS.md) for triage, containment, recovery and follow-up limits.

Security fixes target the current `main` branch. No separate maintained release branches or response-time guarantee are defined.

The plugin can run local hooks and setup tools. Review its source and the hook definition, and approve hooks only through the host's normal trust flow. Never bypass approval or publish local runtime credentials. Apply the [risk-based security contract](assets/global-stack-policy.md#risk-based-security-and-operations) to affected data, permissions, interfaces, dependencies and availability; provenance and scanner results do not certify the absence of vulnerabilities or secrets.
