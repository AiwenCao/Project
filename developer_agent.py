import ast
import ollama


def validate_code(code):
    if not isinstance(code, str):
        raise ValueError("Generated code must be a string.")

    if not code.strip():
        raise ValueError("Generated code must not be empty.")

    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        raise ValueError(
            f"Generated code is not valid Python: {error}"
        )

    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]

    if not functions:
        raise ValueError(
            "Generated code must contain at least one function."
        )

    decide_functions = [
        node for node in functions
        if node.name == "decide_next_move"
    ]

    if not decide_functions:
        raise ValueError(
            "Generated code must contain decide_next_move(state)."
        )

    decide_function = decide_functions[0]

    if len(decide_function.args.args) != 1:
        raise ValueError(
            "decide_next_move must take exactly one parameter: state."
        )

    if decide_function.args.args[0].arg != "state":
        raise ValueError(
            "The parameter of decide_next_move must be named state."
        )

    return code


def run_developer(plan):
    system_prompt = """
You are a Developer Agent.

Your task is to convert a validated robot navigation plan
into working Python code.

Follow these rules strictly:

1. Return ONLY Python source code.
2. Do not include markdown.
3. Do not include code fences.
4. Do not include explanations before or after the code.
5. The generated code MUST contain this public function:

   decide_next_move(state)

6. Other helper functions may exist, but external programs
   must only need to call decide_next_move(state).

7. state is a dictionary with these boolean keys:

   goal_ahead
   goal_on_left
   goal_on_right
   front_blocked
   left_blocked
   right_blocked

8. decide_next_move(state) must return only one of:

   FORWARD
   LEFT
   RIGHT
   STOP

9. The robot must never move into a blocked direction.

10. If the direction toward the goal is unblocked,
    prefer that direction.

11. If the goal direction is blocked, choose another
    safe unblocked direction.

12. If every movement direction is blocked, return STOP.

13. When choosing an alternative safe direction,
    use this priority order:

    FORWARD
    LEFT
    RIGHT

14. Do not use external packages.

15. The generated output must be valid executable Python code.
"""

    response = ollama.Client(timeout=120).chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": str(plan)
            }
        ],
        think=False,
        options={
            "temperature": 0,
            "num_predict": 1024
        }
    )

    code = response["message"]["content"].strip()

    if code.startswith("```python"):
        code = code[len("```python"):]

    if code.startswith("```"):
        code = code[3:]

    if code.endswith("```"):
        code = code[:-3]

    code = code.strip()

    return validate_code(code)

"""APPEND this implementation to your ORIGINAL developer_agent.py; do not replace it."""
import ast as _ast
import json as _json
from pathlib import Path as _Path

REVISION_SYSTEM_PROMPT = '''You are a robot-navigation Developer Agent. Revise the
existing Python decide_next_move(state) function using the user-provided
requirements, planner output, discrete simulation review, and IR-SIM benchmark.
Return ONLY valid Python source defining decide_next_move(state).
State has boolean keys front_blocked, left_blocked, right_blocked, goal_ahead,
goal_on_left, goal_on_right. Return FORWARD, LEFT, RIGHT or STOP.
Avoid blocked routes. Keep compatible with the IR-SIM caller.'''


def run_developer_revision(original_navigation_code, review_notes,
                           benchmark_report, requirements, plan, llm=None,
                           output_path='generated/navigation_logic_revised.py'):
    """llm(system_prompt, user_prompt)->Python source; integrate project LLM caller."""
    if llm is None:
        llm = ollama_llm
    prompt = _json.dumps({'original_code': original_navigation_code,
        'review_notes': review_notes, 'benchmark_report': benchmark_report,
        'requirements': requirements, 'plan': plan}, ensure_ascii=False, default=str)
    code = llm(REVISION_SYSTEM_PROMPT, prompt).strip()
    if code.startswith('```'):
        raise ValueError('Developer revision must return plain Python, not markdown')
    tree = _ast.parse(code)
    if not any(isinstance(node, _ast.FunctionDef) and node.name == 'decide_next_move' for node in tree.body):
        raise ValueError('Revised code must define decide_next_move')
    target = _Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(code + '\n', encoding='utf-8')
    return str(target)


def ollama_llm(system_prompt, user_prompt):
    """Match the original qwen3:8b Ollama setup."""
    response = ollama.Client(timeout=180).chat(
        model="qwen3:8b", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}],
        think=False, options={"temperature": 0, "num_predict": 2048})
    return response["message"]["content"].strip()
