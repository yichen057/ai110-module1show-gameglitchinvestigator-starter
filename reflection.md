# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

When I first ran the game, it was broken in multiple ways across logic, state management, and UI rendering. Through manual testing and code inspection, I found a total of 7 bugs:

Bug 1 (Initial attempt counter starts at 1): The session state initialized `attempts = 1`, so the UI showed "Attempts left: 7" on page load before any input.

Bug 2 (Inverted hint messages): In `check_guess`, the messages were swapped. Guessing too high showed "Go HIGHER!" and guessing too low showed "Go LOWER!", making the game unsolvable.

Bug 3 (Broken New Game reset): The `if new_game:` block only reset `attempts` and `secret`, leaving `status`, `score`, and `history` unchanged. The game immediately hit `st.stop()` after clicking "New Game" because `status` was still `"won"` or `"lost"`.

Bug 4 (Attempts left display lag): `st.info("Attempts left: ...")` was rendered before `attempts += 1`, so it always showed the value from the previous rerun, one step behind.

Bug 5 (Developer Debug Info out of sync): The Debug Info expander was also rendered before the increment, causing its `Attempts` field to disagree with the `Attempts left` value shown above it.

Bug 6 (Test assertions expected a string, not a tuple): The original tests in `test_game_logic.py` asserted `result == "Win"`, but `check_guess` returns a `(outcome, message)` tuple. All three tests failed until unpacked with `outcome, _ = check_guess(...)`.

Bug 7 (`pytest` could not import `logic_utils`): Running `pytest` from the project root raised `ModuleNotFoundError: No module named 'logic_utils'` because pytest did not add the root to `sys.path`. Fixed by adding a `conftest.py` at the project root.

| # | File | Category | Comment location |
|---|---|---|---|
| Bug 1 | `app.py` | Logic: wrong initial state | `app.py:33-34` |
| Bug 2 | `logic_utils.py` | Logic: inverted messages | `logic_utils.py:44-46` |
| Bug 3 | `app.py` | State management: incomplete reset | `app.py:70-72` |
| Bug 4 | `app.py` | Streamlit rendering: display lag | `app.py:51-52` |
| Bug 5 | `app.py` | Streamlit rendering: debug out of sync | `app.py:54-55` |
| Bug 6 | `tests/test_game_logic.py` | Test correctness: tuple vs string | `test_game_logic.py:3-4` |
| Bug 7 | `conftest.py` | Test infrastructure: import error | `conftest.py:1-2` |

---

## 2. How did you use AI as a teammate?

I used Claude Code (Anthropic) as my primary AI assistant throughout this project, using it in both interactive chat mode and headless agent mode (`claude -p`) to refactor code and fix bugs.

**Correct AI suggestion: Refactoring logic into `logic_utils.py`:**
Claude correctly identified that all four functions (`check_guess`, `parse_guess`, `get_range_for_difficulty`, `update_score`) needed to be moved from `app.py` into `logic_utils.py` to replace the `NotImplementedError` stubs. It also fixed the inverted message bug in `check_guess` at the same time, swapping `"Go HIGHER!"` and `"Go LOWER!"` to match the correct direction. I verified this by running `pytest -v`, which showed all 5 `check_guess`-related tests passing, and by manually playing the game and confirming the hints now point in the correct direction.

**Incorrect/misleading AI suggestion: `st.empty()` for the attempts counter:**
Claude suggested using `st.empty()` as a placeholder for the `Attempts left` info box, claiming it would fix the rendering lag. The suggestion was partially correct, and `Attempts left` did update immediately after the fix. However, Claude missed that the Developer Debug Info expander had the same problem: its `Attempts` value was still stale because it was also rendered before the increment. I discovered this by manually comparing the two values in the running app after the first fix was applied. A second `st.empty()` placeholder (`debug_display`) was needed to fully resolve the sync issue.

---

## 3. Debugging and testing your fixes

I used a combination of manual testing (running the Streamlit app) and automated pytest tests to verify each fix.

**Manual testing:** For Bug 1 (initial counter), I refreshed the browser and confirmed the display started at "Attempts left: 8" instead of "Attempts left: 7". For Bug 3 (New Game reset), I played a full game to completion, then clicked "New Game" and verified the game was playable again without a browser refresh. For the `st.empty()` sync fix, I submitted a guess and opened the Developer Debug Info expander to confirm "Attempts" matched "Attempts left" on the same rerun.

**Automated testing:** I ran `pytest -v` after each code change. The key test that caught the inverted hint bug was `test_high_guess_shows_go_lower_message`, which asserted `"LOWER" in message` when `guess=60, secret=50`. Before the fix, this test would have failed because the message said `"Go HIGHER!"`. After the fix it passed, confirming the message direction was corrected. Claude helped design this regression test by suggesting to assert on the message string directly, not just the outcome label, which gave stronger coverage.

---

## 4. What did you learn about Streamlit and state?

The secret number kept changing because the original code called `random.randint(low, high)` unconditionally at the top of the script, with no guard checking whether a secret already existed. Every time the user clicked "Submit", Streamlit re-ran the entire script from top to bottom, and that bare `random.randint` call generated a brand-new secret on every rerun. So the target was literally moving every time you guessed.

Streamlit "reruns" work like this: every user interaction (a button click, a text input change, or a sidebar selection) causes Streamlit to re-execute your entire Python file from line 1. Think of it like pressing F5 on a web page, except Streamlit does it automatically. `st.session_state` is a dictionary that survives across these reruns and is the only place where values persist between script executions. Without it, every variable you define is reset to its initial value on every interaction.

The fix that gave the game a stable secret number was wrapping the `random.randint` call in an `if "secret" not in st.session_state:` guard. This means the secret is only generated once on the very first run and is then stored in `st.session_state.secret`. Every subsequent rerun skips that line entirely and reads the same stored value, which is all it takes to make the game solvable.

---

## 5. Looking ahead: your developer habits

The habit I want to reuse is writing regression tests that assert on message *content*, not just outcome labels. In this project, the inverted-hint bug (`check_guess` returning `"Too High"` with the right label but the wrong message) would have been invisible to a test that only checked `outcome == "Too High"`. Asserting `"LOWER" in message` caught the actual user-facing problem. That principle of testing what the user actually sees, not just the internal category, applies to any project where presentation matters.

The one thing I would do differently next time is to verify the full scope of an AI fix before accepting it. In this project, Claude suggested using `st.empty()` for the `Attempts left` display, which I applied immediately. It fixed that one widget, but I only discovered by manually testing the app that the Developer Debug Info expander had the exact same rendering-lag problem and was not covered by the fix. A quick end-to-end check, or simply asking Claude whether the same pattern appeared elsewhere in the code, would have caught this the first time.

AI-generated code looks polished and confident, but this project showed me that confidence has nothing to do with correctness. The AI produced code that compiled, ran, and even looked reasonable, yet it was broken in seven different ways. The real skill is not prompting the AI to write code but knowing the domain well enough to catch what the AI missed.

