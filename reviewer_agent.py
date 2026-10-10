"""Review the discrete simulation report."""
import json

KEYS = ('issue', 'likely_cause', 'recommendation', 'needs_revision')
SYSTEM_PROMPT = '''Review the robot navigation simulation report. Respond with ONLY
one JSON object containing exactly these keys: issue, likely_cause,
recommendation (strings), needs_revision (boolean). Identify failing scenario
patterns and propose actionable changes. Never invent measured results.'''


def validate_review(data):
    if isinstance(data, str):
        data = json.loads(data)
    if not isinstance(data, dict) or set(data) != set(KEYS):
        raise ValueError(f'Review must have exactly these keys: {KEYS}')
    if any(not isinstance(data[k], str) for k in KEYS[:-1]):
        raise ValueError('Review explanations must be strings')
    if type(data['needs_revision']) is not bool:
        raise ValueError('needs_revision must be boolean')
    return data


def run_reviewer_agent(simulation_report, llm=None):
    if llm is None:
        failed = simulation_report.get('failed_scenarios', 0)
        sample = [r for r in simulation_report.get('results', []) if not r.get('passed', False)][:3]
        return validate_review({'issue': f'{failed} failing scenarios' if failed else 'No discrete test failures',
            'likely_cause': f'Sample failures: {json.dumps(sample, default=str)}' if failed else 'None detected',
            'recommendation': 'Compare generated policy with requirements and correct mismatches' if failed else 'Proceed to IR-SIM',
            'needs_revision': failed > 0})
    result = validate_review(llm(SYSTEM_PROMPT, json.dumps(simulation_report, default=str)))
    # Measured simulation failures are authoritative.
    result['needs_revision'] = simulation_report.get('failed_scenarios', 0) > 0
    return result
