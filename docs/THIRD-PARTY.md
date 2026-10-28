# Upstream components and provenance

| Source | Delivered scope | Version and license |
| --- | --- | --- |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | Six skills, real lifecycle hooks with JS helpers, README, and published benchmark for gain | 5.3.2; [MIT](../licenses/ponytail-LICENSE) |
| [Caveman](https://github.com/JuliusBrussee/caveman) | Base communication skill from the existing local installation | Local snapshot, release version unverified; [Apache-2.0](../licenses/caveman-LICENSE), [NOTICE](../licenses/caveman-NOTICE) |
| [UI-UX-Pro-Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Skill text, data, and Python scripts from CLI assets; no interpreter caches | CLI 2.15.0; [MIT](../licenses/ui-ux-pro-max-LICENSE) |
| [CodeGraph](https://github.com/colbymchenry/codegraph) | Stack-owned guide; runtime remains a local dependency | Package pin and separately observed runtime version in [versions.json](../assets/versions.json) |
| [RTK](https://github.com/rtk-ai/rtk) | Stack-owned guide; runtime remains a local dependency | Official release pin in [versions.json](../assets/versions.json); repair verifies release SHA256 |

All 39 UIUX data files and 28 script/test files from the CLI assets were compared with the installed copy: byte-identical, excluding interpreter caches. The runtime checker performs a real search. This proves the delivered resources, not future upstream completeness. Font/icon provenance files are retained.

Modifications: UIUX skill examples use the directory of the loaded plugin skill file instead of a global installation. In the Ponytail gain skill, only source references were adjusted to the bundled benchmark/README copy. The combined `hooks/hooks.json` adds stack handlers and accepts both host plugin-root variables. Original Ponytail JavaScript files and rules are unchanged. The affected skill texts identify the modifications.

[bundle-manifest.json](../assets/bundle-manifest.json) contains SHA256 hashes of delivered skills, hooks, and licenses. License texts come from the installed Ponytail package or official upstream repositories. Personal runtime paths and credentials do not belong in provenance records.
