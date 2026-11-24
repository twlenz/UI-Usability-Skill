# Cognitive walkthrough reference

The cognitive walkthrough (Wharton, Rieman, Lewis & Polson, 1994; procedure as described by NN/g) checks whether a specific user can complete specific tasks by exploring the interface, without training. It's strongest on learnability and on novel or custom interactions. It adds less on standard patterns users already know (a basic login form), so spend the effort on the UI's own flows.

It complements heuristic evaluation: heuristics sweep the whole screen for general violations, while the walkthrough follows one user through one task and finds where they get stuck. Use both.

## Inputs (from the UI brief)

1. **Persona**: who the user is, what they know (domain knowledge, tech familiarity), what they *don't* know (they haven't seen the code or the designer's intentions), and how they'll approach it (a study participant skims and wants to finish; an expert analyst explores).
2. **Tasks**: the top 1–3 tasks, stated as the user's goal ("Add a new participant and assign them to condition B"), not as UI steps.
3. **Correct action sequence** for each task: the steps the designer intends, one step per discrete action or new screen state.

## Procedure

For each task, go step by step through the correct action sequence. Use the step screenshots (`step-NN-*.png`) where they exist; otherwise reason from the screen the user would be looking at.

At each step, answer four questions *as the persona*:

1. **Will the user try to achieve the right effect?** Given their goal and what's on screen, would they even know this step is needed? (Fails when a required step is unexpected, such as having to "activate" something first or save before export.)
2. **Will the user notice that the correct action is available?** Is the control visible, without hover, scrolling, or opening a menu they have no reason to open? Is it salient enough to be found among everything else?
3. **Will the user associate the correct action with the effect they want?** Does the label/icon/position say "this does what you want," in the persona's vocabulary? Would a competing control look like a better match?
4. **After the action, will the user see that progress was made?** Is there a visible, interpretable change that confirms the step worked and suggests what's next?

Any "no" (or "probably not") fails the step. For each failure, write a **failure story**: one or two sentences on what this persona would plausibly do instead ("She'd look for 'Add' near the table, not in the sidebar, and conclude the feature doesn't exist").

After the last step, record whether the task as a whole succeeds and list the failing steps.

## Staying in character

The evaluator has an unfair advantage: it can read the code. Don't use it during the walkthrough.

- The persona knows only what's on screen and what their background gives them. Variable names, file names and comments are invisible to them.
- The persona doesn't read paragraphs of instructions carefully. If a step only succeeds because the user read and remembered a long instruction block, count that as a failure on Q1 or Q2.
- Hover-only controls, off-screen controls and controls inside unlabeled menus fail Q2 unless something on screen points to them. On touch devices, hover-only controls fail Q2 outright: there's no hover.
- If the step screenshots show the click-through script couldn't find a control (`ok: false` in `audit.json`), that's strong evidence the control isn't where the task expects it; check it against the screenshot.
- Be honest about uncertainty: "probably not" with a reason is more useful than a confident pass.

## Output (per task)

```
Task: Add a participant and assign condition B. Persona: RA, first week on the project
Step 1 — click "Add participant"         Q1 ✓  Q2 ✓  Q3 ✓  Q4 ✗  FAIL
  Form opens below the fold; nothing visible changes at the top of the page. RA clicks again.
Step 2 — enter ID, choose "B"           Q1 ✓  Q2 ✓  Q3 ✗  Q4 ✓  FAIL
  Dropdown is labeled "Group", but the protocol says "condition". RA isn't sure it's the same thing.
Step 3 — click "Save"                   Q1 ✓  Q2 ✓  Q3 ✓  Q4 ✓  PASS
Result: completes with hesitation; 2 failing steps (1, 2)
```

Turn each failing step into a finding in the findings table, with severity ≥ 3 when the task is a top task.
