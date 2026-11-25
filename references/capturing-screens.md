# Capturing screens on non-web platforms

`scripts/capture_web.py` covers anything a browser can load. This file covers the rest. In every case the goal is the same: real pixels of the main states (first view, populated, error, empty) for the evaluator, without changing the user's app in ways that ship.

Save captures into the review directory (`<review-dir>/shots/`), never into the user's project.

Tools used below, and how to get them on Debian/Ubuntu: `xvfb-run` (`apt-get install xvfb`), `import` (`apt-get install imagemagick`), `xdotool` (`apt-get install xdotool`). Check with `which <tool>` first. The same install rule as `capture_web.py` applies: install freely in a sandbox, ask first on the user's own machine, and fall back to a code-only review if you can't.

## Tkinter

**Linux / headless** (no display): run under a virtual display and grab the root window.
```bash
xvfb-run -a -s "-screen 0 1280x800x24" bash -c 'python app.py & APP=$!; sleep 3; import -window root shots/main.png; kill $APP'
```
`import` comes from ImageMagick. If Python's `tkinter` module is missing in the default interpreter, try other installed interpreters (e.g. `/usr/bin/python3.12`), whichever has `_tkinter`.

**macOS / Windows with a display**: use PIL to grab the window's bounding box from a small harness that imports the app's root window, or capture the full screen with `screencapture -x shots/main.png` (macOS; may require Screen Recording permission) and crop.

**Reaching other states**: if the app is structured with a function per screen, a throwaway harness script (in the review dir) can build the root, call the function for the state you need, `root.update()`, then capture. Don't add snapshot code to the app itself.

## PyQt / PySide

Qt can render without any display:
```python
import os; os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PyQt6.QtWidgets import QApplication
app = QApplication([])
win = build_main_window()        # import from the user's module
win.resize(1280, 800); win.show(); app.processEvents()
win.grab().save("shots/main.png")
```
`QWidget.grab()` works per widget, so dialogs and individual states can be captured the same way.

## Electron

Playwright drives Electron directly (`playwright._electron.launch(args=["main.js"])`), then use `window.screenshot(...)`. If the renderer is plain HTML, you can often point `capture_web.py` at the renderer's `index.html` instead.

## Experiment software

- **jsPsych / lab.js / any browser-based experiment**: use `capture_web.py` with `--steps`, using key presses (`{"action": "press", "value": "f"}`) to advance through instructions and trials.
- **PsychoPy**: `win.getMovieFrame(); win.saveMovieFrames("shots/screen.png")` after a `win.flip()`, in a throwaway harness that draws the screen you want. Run windowed (`fullscr=False`) and, on headless Linux, under `xvfb-run`.
- **pygame**: `pygame.image.save(screen, "shots/screen.png")` after drawing a frame. On headless Linux set `SDL_VIDEODRIVER=dummy`.

## Mobile

- **Expo / React Native Web / Flutter web**: run the web target and use `capture_web.py --steps-on both` (its mobile pass emulates a real phone, with touch input and no hover). Pick the device with `--mobile-device`. Web builds approximate native behavior, so use the simulator for anything platform-specific.
- **iOS simulator**: `xcrun simctl io booted screenshot shots/main.png`.
- **Android emulator/device**: `adb exec-out screencap -p > shots/main.png`.

## Terminal UIs

- Plain CLIs: capture the transcript (`script -q`, or run with sample input and save stdout/stderr). The evaluator works from text.
- **Textual**: `app.save_screenshot()` or `textual run --screenshot`. **Rich**: `Console(record=True)` then `console.save_svg(...)`.

## When you can't capture

If rendering needs things you shouldn't install or run (hardware, credentials, a remote service), evaluate from code. Tell the evaluator the review is code-only, and say so in the final report. A code-only review can't judge visual hierarchy, salience or layout consistency reliably, and the report shouldn't imply it did.
