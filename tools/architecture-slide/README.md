# Quellen der Architekturfolie

`build.mjs` ist die urspruengliche Quelle der editierbaren PowerPoint-Folie
`docs/KISS-Chris-Stack_Architektur-OnePager.pptx`.
`preview.png` und `validation-final.json` dokumentieren den damaligen Export.

Das Build-Skript ist unveraendert uebernommen. Es benoetigt `@oai/artifact-tool`
und verweist noch auf die lokale Codex-Laufzeit sowie die urspruenglichen
Arbeits- und Ausgabepfade. Es ist daher noch kein portabler Repository-Build.
Die Validierungsdatei ist historische Export-Evidence, kein neuer Testlauf.

Die Folie beschreibt den Paketstand 2026.10.05 mit Fast-/Deep-Path-Routing.
Die spaeter global festgelegte Fast-Path-only-Regel ist darin noch nicht enthalten.
