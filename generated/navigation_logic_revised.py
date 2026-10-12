def decide_next_move(state):
    # Check if goal is directly ahead and path is clear
    if state['goal_ahead'] and not state['front_blocked']:
        return 'FORWARD'
    
    # Check if goal is on the left and path is clear
    if state['goal_on_left'] and not state['left_blocked']:
        return 'LEFT'
    
    # Check if goal is on the right and path is clear
    if state['goal_on_right'] and not state['right_blocked']:
        return 'RIGHT'
    
    # Check if all directions are blocked
    if state['front_blocked'] and state['left_blocked'] and state['right_blocked']:
        return 'STOP'
    
    # If no goal is directly ahead, check for any unblocked direction
    if not state['front_blocked']:
        return 'FORWARD'
    if not state['left_blocked']:
        return 'LEFT'
    if not state['right_blocked']:
        return 'RIGHT'
    
    # If all directions are blocked, stop
    return 'STOP'
