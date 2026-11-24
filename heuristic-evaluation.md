# Heuristic evaluation reference

Used by the evaluator. Primary set: Nielsen's 10 usability heuristics (NN/g). Supplementary sets: Tognazzini's First Principles of Interaction Design, an explicit visual-hierarchy check, and, for web UIs, Vercel's web interface guidelines (`web-interface-guidelines.md`). Severity: Nielsen's 0–4 scale.

For each heuristic, the "look for" items are the specific ways generated UIs tend to violate it. They're prompts for looking, not a checklist to tick: report only what you actually observe.

## Nielsen's 10 heuristics

**H1. Visibility of system status.** Keep users informed about what's happening, with timely feedback.
Look for: buttons that do something with no visible result; no loading/progress state for slow operations; no saved/unsaved indicator where work can be lost; current page/step/tab not highlighted; active filters or modes not shown; feedback that appears off-screen or far from where the user acted.

**H2. Match between system and the real world.** Use the user's words and concepts, in a natural order.
Look for: developer vocabulary in labels (`id`, `null`, `config`, `payload`, snake_case, raw enum values); internal error text; order of fields or steps that doesn't follow the user's real workflow; icons whose meaning depends on knowing the code; controls whose layout doesn't map to what they affect.

**H3. User control and freedom.** Clearly marked exits; undo and redo.
Look for: no way to cancel or go back from a flow; destructive actions with no undo; modals with no close; irreversible actions one click away; wizards that lose data when stepping back.

**H4. Consistency and standards.** Same words, same looks, same places for the same things; follow platform conventions.
Look for: the same action styled differently on different screens; the primary action in different positions; mixed label styles (some above, some beside); the same concept called by two names; non-standard behavior for standard-looking controls; more than ~3–4 font sizes or button styles without a role reason (check `audit.json`).

**H5. Error prevention.** Eliminate error-prone conditions or confirm before commitment.
Look for: free-text where a constrained input would prevent errors (dates, numbers, IDs with a format); validation only after submit; destructive buttons adjacent to frequent ones; double-submit possible; defaults that are wrong for most users.

**H6. Recognition rather than recall.** Make options, actions and needed information visible.
Look for: icon-only buttons without visible labels (check `audit.json`); placeholder text used as the only label (disappears on typing); instructions on one screen needed on another; hidden actions that only appear on hover; required formats not shown at the field; keyboard shortcuts that must be memorized.

**H7. Flexibility and efficiency of use.** Accelerators for experienced users that don't get in novices' way.
Look for: frequent tasks needing many clicks; no keyboard support (Enter to submit, Tab order); no bulk actions where users handle many items; no sensible defaults or remembered last values. (For one-time users such as study participants this heuristic matters less.)

**H8. Aesthetic and minimalist design.** Every extra unit of information competes with the relevant ones.
Look for: explanatory paragraphs, welcome banners, taglines, restated labels; more than ~150 words of non-data text on a working screen (check `audit.json` word counts and longest blocks); decorative elements more salient than content; everything given equal visual weight; boxes nested in boxes.

**H9. Help users recognize, diagnose, and recover from errors.** Plain-language error messages that say what's wrong and how to fix it.
Look for: generic "Error" or "Invalid input"; error shown far from the field; error that clears the user's input; raw exceptions or codes; no suggested fix.

**H10. Help and documentation.** Ideally unnecessary; when needed, concise, task-focused and in context.
Look for: a UI that only works if you read a long help block (that's an H8/H6 problem in disguise); no help at all for genuinely unfamiliar concepts; help detached from where it's needed.

## Tognazzini's First Principles (supplementary)

Use these to catch what Nielsen's set doesn't make explicit:

- **Anticipation**: everything needed for each step is on screen at that step.
- **Autonomy**: user feels in control; status info is visible, current and truthful.
- **Color**: never the only carrier of meaning; pair with text, icon, shape or position.
- **Consistency (levels and induced inconsistency)**: consistency matters most for small controls and behavior; things that act differently should look different.
- **Defaults**: easy to overwrite; avoid one when no choice clearly wins; reset controls say exactly what they reset.
- **Discoverability**: hiding needed controls doesn't simplify, it adds complexity. A clean look is no excuse to hide functions on large screens.
- **Explorable interfaces**: clear default path, stable "home" cues, reversible actions, a way out of every task.
- **Fitts's law**: important targets big and close; fewer targets per task.
- **Latency reduction**: acknowledge input immediately; progress feedback for longer waits; ignore duplicate clicks.
- **Protect users' work**: no data loss from errors, navigation, refresh or crashes; preserve in-progress input.
- **Readability**: high contrast, adequate size; data more prominent than its labels; key words first in labels.
- **Simplicity**: remove the unnecessary rather than hide the necessary; progressive disclosure for advanced features.
- **Visible navigation**: stable frame, current location highlighted.

## Visual hierarchy (supplementary)

Nielsen's set only touches hierarchy under H8, and Tognazzini's under Readability. Check it explicitly, because "everything looks equally important" is a common failure in generated UIs.

Do the **squint test**: look at each screenshot at reduced size or blurred, and note what stands out first, second and third. Then compare that order with the importance order in `ui-brief.md` (primary action, most important data).

Look for:
- No clear first-read element, or the most salient thing is decoration, a banner or a secondary control rather than the primary action or key data.
- Primary and secondary actions with the same visual weight, or a destructive action as prominent as the primary one.
- Headings, labels and body text with weak size/weight separation, so the structure doesn't show. Heading levels that skip or don't match the nesting.
- Everything in boxes of the same weight, or several competing focal points on one screen.
- Scan order (top-left first in left-to-right layouts) that doesn't follow importance, so the key number or action sits low or far right.
- Labels more prominent than the data they label.
- Hierarchy that differs between screens (the primary action is bold on one screen and muted on the next).

File findings under H8 (or H4 for cross-screen differences), with "Visual hierarchy" in the Principle column. A code-only review can't judge this; list it under "Not assessed".

## Web interface guidelines (web UIs only)

When the UI is a web page or app, also check it against `web-interface-guidelines.md` (Vercel's guidelines): keyboard and focus, zoom and paste, forms, states, loading and layout shift, motion. Most items are checked in the code step. File each violation under its closest Nielsen heuristic.

## Severity scale (Nielsen)

| Sev | Meaning | Action |
|---|---|---|
| 0 | Not a usability problem | — |
| 1 | Cosmetic | Fix if time allows |
| 2 | Minor | Low priority |
| 3 | Major | Fix before delivering |
| 4 | Catastrophe | Must fix; the task fails or data is lost |

Judge from three factors together:
- **Frequency**: how many users, how often (every visit vs. one edge case).
- **Impact**: how hard it is to overcome (slows them vs. blocks them vs. loses work).
- **Persistence**: whether users get past it once they've learned (one-time confusion vs. trips them up every time).

Context shifts severity. A confusing label on a screen participants see once with no help available is worse than the same label in a daily tool the user built for themselves. Any cognitive walkthrough step failure on a top task is at least a 3.

Severity judgments vary between evaluators even among experts, so give a one-clause reason with each rating to make it checkable.

## How the three target problems map

| Problem | Primary heuristics | Walkthrough question that catches it |
|---|---|---|
| Unclear controls | H2, H4, H6, Tog: Discoverability, Readability | Q2 (notice it), Q3 (associate it with the goal) |
| Text overload | H8, H10, Tog: Simplicity | Q2 (the action is buried), Q4 (feedback drowned out) |
| Inconsistent layouts | H4, Tog: Consistency, Visible navigation | Q2 (action isn't where the last screen taught them to look) |
| Flat or competing hierarchy | H8, Visual hierarchy, Tog: Readability | Q2 (the right action doesn't stand out) |

## Not used: SUS and other user questionnaires

The System Usability Scale and similar questionnaires measure real users' perceptions after they've used the system. An evaluator rating SUS items on a user's behalf would produce a number that looks like validated measurement but isn't one, so don't produce SUS, UMUX, or NASA-TLX scores here. If the project itself is a study or usability test, those instruments may belong *in* the UI. That's a feature request, not part of this evaluation.
