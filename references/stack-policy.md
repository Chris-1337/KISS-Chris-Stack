# KISS-Chris-Stack policy

## Optimization targets

| Component | Primary optimization | Must not replace |
| --- | --- | --- |
| Ouroboros | intent clarity, execution control, evaluation, repair | repository understanding or code minimality |
| CodeGraph | repository context and impact analysis | requirements or implementation policy |
| UI-UX-Pro-Max | UI structure, visual quality, interaction, responsiveness, and accessibility guidance | user requirements or project rules |
| Ponytail | minimal necessary code | correctness, validation, security, accessibility |
| Caveman | minimal agent prose | code changes |
| RTK | minimal command/tool output | required evidence |

## Recommended decision tree

1. Is the task fully explicit and local?
   - Yes: fast path.
   - No: continue.
2. Does the task cross multiple modules, alter architecture, have ambiguous requirements, or need explicit acceptance criteria?
   - Yes: deep path with Ouroboros.
   - No: fast path.
3. Is the deep-path goal genuinely ambiguous?
   - Yes: use interview/auto to converge on a Seed.
   - No: execute the testable Seed directly without another interview.
4. If the task changes an interface, use UI-UX-Pro-Max; skip it for non-visual work.
5. Bound execution to three iterations per acceptance criterion, 15 minutes without progress, and 60 minutes per generation unless an extension is reported.
6. Regardless of path, use the other layers only for their stated role.
7. Never optimize away required verification.
