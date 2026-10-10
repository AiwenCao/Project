"""Exhaustive discrete input simulation of the generated navigation function."""
import itertools
import json
from pathlib import Path

FLAGS = ('front_blocked', 'left_blocked', 'right_blocked')
GOALS = ('goal_ahead', 'goal_on_left', 'goal_on_right')
ACTIONS = {'FORWARD', 'LEFT', 'RIGHT', 'STOP'}


def expected_action(state):
    """Reference policy; update to match your approved planner specification."""
    if not state['front_blocked'] and state['goal_ahead']:
        return 'FORWARD'
    if state['goal_on_left'] and not state['left_blocked']:
        return 'LEFT'
    if state['goal_on_right'] and not state['right_blocked']:
        return 'RIGHT'
    if not state['front_blocked']:
        return 'FORWARD'
    if not state['left_blocked']:
        return 'LEFT'
    if not state['right_blocked']:
        return 'RIGHT'
    return 'STOP'


def create_scenarios():
    """8 obstacle combinations x 8 goal-flag combinations = 64 cases."""
    for blocks in itertools.product((False, True), repeat=3):
        for goal_flags in itertools.product((False, True), repeat=3):
            state = dict(zip(FLAGS, blocks))
            state.update(dict(zip(GOALS, goal_flags)))
            yield state


def run_simulation(decide_next_move=None, expected_fn=expected_action):
    if decide_next_move is None:
        from generated.navigation_logic import decide_next_move
    rows = []
    for state in create_scenarios():
        expected = expected_fn(state)
        try:
            actual = decide_next_move(state)
            error = None
        except Exception as exc:
            actual = None
            error = f'{type(exc).__name__}: {exc}'
        passed = actual == expected and actual in ACTIONS
        rows.append({'state': state, 'expected': expected, 'actual': actual,
                     'passed': passed, 'error': error})
    total = len(rows)
    passed = sum(row['passed'] for row in rows)
    return {'total_scenarios': total, 'passed_scenarios': passed,
            'failed_scenarios': total - passed, 'success_rate': passed / total if total else 0,
            'results': rows}


def main():
    report = run_simulation()
    path = Path('artifacts/simulation_report.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}, indent=2))
    return report


if __name__ == '__main__':
    main()
