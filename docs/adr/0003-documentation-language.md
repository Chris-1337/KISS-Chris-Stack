# ADR 0003: English documentation and prompt-language communication

- Status: accepted through the user request dated 2026-10-28.
- Decision: All existing and future documentation, including human documentation, ADRs, and agent traces, uses English. Internal reasoning uses English. User-facing communication follows the language of the user's prompt, including German for German prompts.
- Implementation: The [shared policy](../../assets/global-stack-policy.md) is the canonical language rule; setup distributes it through the existing managed global block. Documentation bootstrap follows the same rule.
- Preservation: Translate prose without changing technical meaning, historical evidence, paths, commands, links, upstream license texts, or unrelated changes. Existing German filenames are retained to preserve references.
- Verification: Documentation contracts check English onboarding topics, the language rule, and remaining known German prose. Existing configuration and lifecycle regressions cover preservation behavior; independent evaluation reviews translation completeness and meaning.
