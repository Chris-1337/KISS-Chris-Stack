# Contributing

Use Issues for reproducible bugs and concrete feature requests, and Discussions for questions and ideas. Do not post credentials or vulnerability details publicly; follow [the security policy](SECURITY.md).

Fork this repository and open a pull request against `main`. Describe the problem, the smallest complete change, and relevant checks. Follow [AGENTS.md](AGENTS.md), preserve upstream notices, and write documentation in English.

Project-original material uses the [MIT license](LICENSE). Bundled third-party components retain their [own licenses and notices](docs/THIRD-PARTY.md).

Every community pull request requires review and approval from the owner, `@Chris-1337`. The owner has admin access and may push or merge directly without a pull request. No other collaborator currently has write access. The prepared GitHub ruleset requires one code-owner approval and dismisses stale approvals when changed commits are pushed; activation depends on the release gates in [publication setup](docs/GITHUB-PUBLICATION.md).

Run the relevant repository checks before submitting:

```powershell
uv run --offline --with pytest python -m pytest tests/test_managed_configuration.py tests/test_plugin_lifecycle.py -q
```

Review the complete proposed diff, including new files, for secrets before committing. Ignore rules and automated scanning reduce mistakes but cannot prove that arbitrary confidential information is absent.
