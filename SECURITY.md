# Security policy

Report suspected vulnerabilities privately through [GitHub private vulnerability reporting](https://github.com/Chris-1337/KISS-Chris-Stack/security/advisories/new) once it is enabled for the public repository. While that reporting channel is unavailable, do not create a public issue or discussion containing exploit details or secrets. A separate private contact address has not been designated.

Never include passwords, access tokens, private keys, personal configuration, or unredacted logs in issues, discussions, or pull requests. If a real credential is exposed, revoke or rotate it first; deleting a file or rewriting Git history does not invalidate the credential.

Security fixes target the current `main` branch. No separate maintained release branches or response-time guarantee are defined.

The plugin can run local hooks and setup tools. Review its source and the hook definition, and approve hooks only through the host's normal trust flow. Never bypass approval or publish local runtime credentials.
