# Contributing

Use Issues for reproducible bugs and concrete feature requests, and Discussions for questions and ideas. Do not post credentials or vulnerability details publicly; follow [the security policy](SECURITY.md).

Fork this repository and open a pull request against `main`. Describe the problem, the smallest complete change, and relevant checks. Follow [AGENTS.md](AGENTS.md), preserve upstream notices, and write documentation in English.

Project-original material uses the [MIT license](LICENSE). Bundled third-party components retain their [own licenses and notices](docs/THIRD-PARTY.md).

Every community pull request requires review and approval from the owner, `@Chris-1337`. The owner has admin access and may push or merge directly without a pull request. No other collaborator currently has write access. The active GitHub ruleset requires one code-owner approval and dismisses stale approvals when changed commits are pushed; see [publication setup](docs/GITHUB-PUBLICATION.md).

Run the relevant repository checks before submitting:

```powershell
uv run --python 3.13 --with pytest python -m pytest tests -q
```

The CI workflow defines this full suite on Windows and Linux with Python 3.13 and Node 24; a workflow definition is not a hosted run receipt. Use `--offline` locally only when dependencies are already cached. Authenticated Codex/model scenarios are a separate explicit opt-in check; see [host observations and their evidence limits](docs/HOST-TESTS.md). Keep criterion/assertion/source evidence under [lifecycle guidance](docs/LIFECYCLE.md), and use [delivery and recovery](docs/DELIVERY.md) for separately authorized releases. A passing development check does not authorize publication.

Review the complete proposed diff, including new files, for secrets before committing. Ignore rules and automated scanning reduce mistakes but cannot prove that arbitrary confidential information is absent.
