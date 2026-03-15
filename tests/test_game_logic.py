from logic_utils import check_guess, parse_guess, update_score

# FIX (Bug 2): Updated assertions to unpack (outcome, message) tuple returned by check_guess.
# Previously tests expected a plain string; fixed in collaboration with Claude Code.
def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

# FIX (Bug 2): Same tuple-unpack fix applied here.
def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

# FIX (Bug 2): Same tuple-unpack fix applied here.
def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

# FIX (Bug 2 regression): Added in collaboration with Claude Code to ensure the inverted
# hint bug never silently regresses. Tests the message content directly.
def test_high_guess_shows_go_lower_message():
    # guessing 60 when secret is 50 should tell the user to go LOWER, not HIGHER
    _, message = check_guess(60, 50)
    assert "LOWER" in message, f"Expected 'LOWER' in message, got: {message}"

# FIX (Bug 2 regression): Symmetric counterpart — covers the other direction of the same bug.
def test_low_guess_shows_go_higher_message():
    # guessing 40 when secret is 50 should tell the user to go HIGHER, not LOWER
    _, message = check_guess(40, 50)
    assert "HIGHER" in message, f"Expected 'HIGHER' in message, got: {message}"

# --- parse_guess tests ---

def test_parse_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None

def test_parse_empty_string():
    ok, _, err = parse_guess("")
    assert ok is False
    assert "Enter a guess" in err

def test_parse_non_number():
    ok, _, err = parse_guess("abc")
    assert ok is False
    assert "not a number" in err

def test_parse_float_truncates():
    # floats should be truncated to int, not rounded
    ok, value, _ = parse_guess("7.9")
    assert ok is True
    assert value == 7

# --- update_score tests ---

def test_win_score_increases():
    result = update_score(0, "Win", 1)
    assert result > 0

def test_too_low_score_decreases():
    result = update_score(50, "Too Low", 1)
    assert result == 45  # 50 - 5
