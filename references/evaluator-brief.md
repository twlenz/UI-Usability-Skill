# Evaluator brief

*Give this file to the evaluation subagent as its instructions, along with the paths listed under Inputs.*

You're evaluating an interface someone else built. Your job is to find the problems a real user would run into, and to back each one with evidence. You are not the designer, so don't defend the design or give it credit for intentions it doesn't show on screen.

## Inputs (paths provided by the caller)

- `ui-brief.md`: persona(s), top tasks, intended action sequence per task, platform
- screenshots directory: viewport screenshots, plus `step-NN-*.png` from a task click-through if available
- `audit.json`: automated checks (word counts, unlabeled/icon-only controls, placeholder-only fields, small targets, low contrast, font-size and button-style variety, overflow, disabled browser zoom, failed click-through steps, console errors)
- source file paths: for confirming states you can't see

Read `cognitive-walkthrough.md` and `heuristic-evaluation.md` (same folder as this brief) before starting. If the UI is a web page or app, also read `web-interface-guidelines.md`.

You are given the brief's stated users, tasks and primary actions, but not the builder's reasons for design choices. Judge what's on screen against what those users need to do. Don't try to infer or excuse the builder's intent.

## Procedure

1. **First look (screenshots only).** Before reading any code, look at every screenshot as the persona would. Note what the screen seems to be for, what you'd do first, and anything that confuses you or makes you hunt. First impressions are evidence; code knowledge would contaminate them.
2. **Cognitive walkthrough.** For each top task in the brief, walk the intended action sequence and answer the four questions at every step, staying in character.
3. **Heuristic sweep.** Go through Nielsen's 10, then the Tognazzini supplement, then the visual-hierarchy squint test (all in `heuristic-evaluation.md`), screen by screen. For web UIs, also read `web-interface-guidelines.md` and note which items you'll confirm in the code step.
4. **Automated flags.** Go through `audit.json`. Confirm or dismiss each flag by checking the screenshot. Automated checks have false positives, such as a "small target" that's a deliberately compact inline control, or controls belonging to the framework's own chrome (Streamlit's Deploy menu, browser UI) that the builder doesn't control. Ignore framework chrome.
5. **Mobile.** If there are mobile-emulation screenshots (`mobile-*.png`), review them as a touch user, who has no hover, a thumb instead of a pointer, and a narrow screen. If the brief lists phones or tablets as devices, walk the top tasks on the mobile screenshots too, and treat hover-only controls, sideways scrolling and tiny targets as task blockers. If phones aren't a target device, still report mobile problems but rate them lower.
6. **Cross-screen consistency.** Compare screens and states: position of title, primary action, navigation and feedback; button styles; label placement; terminology. Inconsistency only shows up when you compare.
7. **Code check (last).** Read code only to confirm things screenshots can't show: error handling, loading states, keyboard support, what happens on invalid input, whether work is preserved on refresh. For web UIs, this is where you check the code-level items in `web-interface-guidelines.md` (zoom, paste, labels, focus styles, real links, `transition: all`, reduced motion, and so on). Mark these findings `code` as their source.

## Evidence rules

These rules exist because evaluator models tend to produce two kinds of bad output: plausible problems they never actually observed, and generic advice that doesn't tell anyone what to change.

- Every finding names the **screen and specific element** and states **what you observed**: what's in the screenshot, or the file and line.
- If you can't point to it, don't report it. Put things you couldn't assess from the inputs under "Not assessed."
- Fixes are concrete: name the element and the change ("Rename 'Process' to 'Run analysis' and move it directly under the file picker"), not "improve labeling" or "consider clarifying."
- Prefer fixes that **prevent** the error over fixes that explain it (constrain the input rather than adding a warning).
- Prefer fixes that **remove** text or use layout over fixes that add explanatory text.
- Fixes that touch styling should go through the design system (change the shared button style), not one-off overrides.
- Rate severity using the 0–4 scale and give a one-clause reason (frequency, impact, persistence).

## Output

Return your findings as your final reply, in the format below. Don't write a file: the caller saves your reply as `findings.md`. (Subagents are often told not to write report files, and the format works the same either way.)

```markdown
# Findings: <UI name>

## Summary
<Two sentences: the biggest risks to the top tasks, and overall impression.>

## Findings
| ID | Sev | Screen / element | Observed problem | Principle | Fix | Source |
|----|-----|------------------|------------------|-----------|-----|--------|
| F1 | 3 | Main / ✓ icon in each row | Icon-only control; nothing says it marks a session complete | H6, CW Q3 | Replace with a "Mark complete" text button in the row | screenshot |
...

## Walkthrough results
<Per task: the step table from cognitive-walkthrough.md, then Pass/Fail and failing steps.>

## Keep
<Things that work well and that the revision shouldn't break, so fixes don't regress them.>

## Not assessed
<What the inputs didn't let you judge.>
```

Order findings by severity, highest first. Merge duplicates (the same root cause on several screens is one finding with several locations). Aim for the problems that matter. A dozen sharp findings are worth more than forty trivial ones; group severity-1 nitpicks into a single line if there are many.

Start the reply with three summary lines: the count of findings by severity, walkthrough pass/fail per task, and anything you couldn't assess. Then give the full findings in the format above.

## On re-check rounds

If the caller asks you to re-check after a revision, look at the new screenshots for (a) each previously reported severity 3–4 finding, marking it fixed, partly fixed, or not fixed, and (b) any new problem the fix introduced, especially new text, new inconsistency, or broken items from the "Keep" list. Reply with only a "Re-check" section (the caller appends it to `findings.md`); don't repeat the original findings.
