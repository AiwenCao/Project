import pytest
from generated.navigation_logic import decide_next_move

@pytest.mark.parametrize("state, expected", [
    # All paths blocked, no goal ahead
    ({'front_blocked': True, 'left_blocked': True, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'STOP'),
    # Goal ahead, front unblocked
    ({'front_blocked': False, 'left_blocked': True, 'right_blocked': True, 'goal_ahead': True, 'goal_on_left': False, 'goal_on_right': False}, 'FORWARD'),
    # Goal on left, left unblocked
    ({'front_blocked': True, 'left_blocked': False, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': True, 'goal_on_right': False}, 'LEFT'),
    # Goal on right, right unblocked
    ({'front_blocked': True, 'left_blocked': True, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': True}, 'RIGHT'),
    # Goal ahead, front blocked but left unblocked
    ({'front_blocked': True, 'left_blocked': False, 'right_blocked': True, 'goal_ahead': True, 'goal_on_left': False, 'goal_on_right': False}, 'LEFT'),
    # Goal on left, left blocked but right unblocked
    ({'front_blocked': True, 'left_blocked': True, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': True, 'goal_on_right': False}, 'RIGHT'),
    # Goal on right, right blocked but front unblocked
    ({'front_blocked': False, 'left_blocked': True, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': True}, 'FORWARD'),
    # Goal ahead, front and left blocked, right unblocked
    ({'front_blocked': True, 'left_blocked': True, 'right_blocked': False, 'goal_ahead': True, 'goal_on_left': False, 'goal_on_right': False}, 'RIGHT'),
    # Goal on left, left and right blocked, front unblocked
    ({'front_blocked': False, 'left_blocked': True, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': True, 'goal_on_right': False}, 'FORWARD'),
    # Goal on right, right and front blocked, left unblocked
    ({'front_blocked': True, 'left_blocked': False, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': True}, 'LEFT'),
    # All paths unblocked, goal ahead
    ({'front_blocked': False, 'left_blocked': False, 'right_blocked': False, 'goal_ahead': True, 'goal_on_left': False, 'goal_on_right': False}, 'FORWARD'),
    # All paths unblocked, goal on left
    ({'front_blocked': False, 'left_blocked': False, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': True, 'goal_on_right': False}, 'LEFT'),
    # All paths unblocked, goal on right
    ({'front_blocked': False, 'left_blocked': False, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': True}, 'RIGHT'),
    # All paths unblocked, no goal
    ({'front_blocked': False, 'left_blocked': False, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'FORWARD'),
    # Front unblocked, no goal
    ({'front_blocked': False, 'left_blocked': True, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'FORWARD'),
    # Left unblocked, no goal
    ({'front_blocked': True, 'left_blocked': False, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'LEFT'),
    # Right unblocked, no goal
    ({'front_blocked': True, 'left_blocked': True, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'RIGHT'),
    # Front and left unblocked, no goal
    ({'front_blocked': False, 'left_blocked': False, 'right_blocked': True, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'FORWARD'),
    # Front and right unblocked, no goal
    ({'front_blocked': False, 'left_blocked': True, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'FORWARD'),
    # Left and right unblocked, no goal
    ({'front_blocked': True, 'left_blocked': False, 'right_blocked': False, 'goal_ahead': False, 'goal_on_left': False, 'goal_on_right': False}, 'LEFT'),
])
def test_decide_next_move(state, expected):
    assert decide_next_move(state) == expected
