"""Benchmark evaluation: measured booleans override LLM interpretations."""
import json

STR_FIELDS = ('issue', 'likely_cause', 'recommendation')
BOOL_FIELDS = ('safety_passed', 'goal_completion_passed', 'efficiency_passed', 'needs_revision')
SYSTEM_PROMPT = '''Inspect the supplied IR-SIM report and preliminary deterministic
assessment. Respond with one JSON object with exactly these keys:
issue, likely_cause, recommendation (strings), safety_passed,
goal_completion_passed, efficiency_passed, needs_revision (booleans).
Be precise about failed worlds and correctable issues; do not invent results.'''


def validate_benchmark_review(value):
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict) or set(value) != set(STR_FIELDS + BOOL_FIELDS):
        raise ValueError('Benchmark review has wrong fields')
    if any(not isinstance(value[k], str) for k in STR_FIELDS):
        raise ValueError('Explanation fields must be strings')
    if any(type(value[k]) is not bool for k in BOOL_FIELDS):
        raise ValueError('Status fields must be boolean')
    return value


def build_deterministic_review(report):
    rows = report.get('results', [])
    unsafe = any(r.get('collision_or_done', False) and not r.get('reached_goal', False) for r in rows)
    successful = report.get('success_rate', 0) >= 1.0 and report.get('total_worlds', 0) > 0
    efficient = report.get('inefficient_success_worlds', 0) == 0 and report.get('efficiency_rate', 0) >= 1.0 and report.get('total_worlds', 0) > 0
    if unsafe:
        issue = 'Unsafe benchmark behavior detected'
        fix = 'Improve obstacle avoidance and collision margins.'
    elif not successful:
        issue = 'Goal completion failure'
        fix = 'Inspect unsuccessful world trajectories and revise goal-seeking and obstacle handling.'
    elif not efficient:
        issue = 'Successful but inefficient navigation'
        fix = 'Reduce unnecessary turns and excessive path lengths.'
    else:
        issue, fix = 'All benchmark checks passed', 'No revision required.'
    return validate_benchmark_review({'issue': issue, 'likely_cause': 'Derived from recorded per-world metrics',
        'recommendation': fix, 'safety_passed': not unsafe,
        'goal_completion_passed': successful, 'efficiency_passed': efficient,
        'needs_revision': unsafe or not successful or not efficient})


def run_benchmark_reviewer_agent(report, llm=None):
    measured = build_deterministic_review(report)
    if llm is None:
        return measured
    result = validate_benchmark_review(llm(SYSTEM_PROMPT, json.dumps({'benchmark_report': report, 'measured': measured}, default=str)))
    result.update({key: measured[key] for key in BOOL_FIELDS})
    return result
