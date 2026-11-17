"""
Tests for the main menu shown by 'python main.py'.
"""

import main


def _feed(monkeypatch, answers):
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))


def test_menu_rejects_invalid_option_and_exits(monkeypatch, capsys):
    _feed(monkeypatch, ["9", "5"])
    main.main_menu()
    out = capsys.readouterr().out
    assert "Invalid option '9'" in out
    assert "Goodbye" in out


def test_menu_runs_an_action_and_returns_to_menu(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(main, "show_quarantine", lambda: calls.append("quarantine"))
    # Option 4, Enter to return to the menu, then exit
    _feed(monkeypatch, ["4", "", "5"])
    main.main_menu()
    assert calls == ["quarantine"]


def test_menu_shows_error_and_continues(monkeypatch, capsys):
    def failing_action():
        raise main.BusBidderError("Example failure")
    monkeypatch.setattr(main, "cancel_session", failing_action)
    _feed(monkeypatch, ["2", "", "5"])
    main.main_menu()
    out = capsys.readouterr().out
    assert "Error: Example failure" in out
    assert "Goodbye" in out
