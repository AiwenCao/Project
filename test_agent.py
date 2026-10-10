"""LLM-backed pytest generation with strict, lightweight validation."""
import ast
import json
import re

SYSTEM_PROMPT = '''Generate executable Python pytest source code for
from generated.navigation_logic import decide_next_move.
The function accepts one dictionary containing boolean flags front_blocked,
left_blocked, right_blocked, goal_ahead, goal_on_left, goal_on_right and returns
one of FORWARD, LEFT, RIGHT, STOP. Cover all obstacle combinations, conflicting
or missing goal flags, and blocked routes. Use pytest.mark.parametrize and assert.
Return ONLY Python source code, with no markdown fences or explanations.'''


def validate_test_code(code):
    if not isinstance(code, str) or not code.strip():
        raise ValueError('Empty test code')
    if '```' in code:
        raise ValueError('Markdown fences are not permitted')
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise ValueError(f'Invalid Python: {exc}') from exc
    if not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree)):
        raise ValueError('Missing import')
    if not any(isinstance(n, ast.Assert) for n in ast.walk(tree)):
        raise ValueError('Missing assert')
    if not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_') for n in ast.walk(tree)):
        raise ValueError('Missing pytest test function')
    if 'decide_next_move' not in code:
        raise ValueError('Tests must call decide_next_move')
    return code


def run_test_agent(requirements, plan, navigation_code='', llm=None):
    """llm(system_prompt, user_prompt) -> raw source string."""
    if llm is None:
        from developer_agent import ollama_llm
        llm = ollama_llm
    prompt = json.dumps({'requirements': requirements, 'plan': plan,
                         'navigation_code': navigation_code}, ensure_ascii=False, default=str)
    return validate_test_code(llm(SYSTEM_PROMPT, prompt))
