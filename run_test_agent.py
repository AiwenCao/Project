"""Generate automated tests using the local Qwen model."""
import json
from pathlib import Path
from test_agent import run_test_agent


def main():
    requirements = json.loads(Path("artifacts/requirements.json").read_text(encoding="utf-8"))
    plan = json.loads(Path("artifacts/plan.json").read_text(encoding="utf-8"))
    navigation_code = Path("generated/navigation_logic.py").read_text(encoding="utf-8")
    code = run_test_agent(requirements, plan, navigation_code)
    output = Path("generated/test_navigation_logic.py")
    output.parent.mkdir(exist_ok=True)
    output.write_text(code.rstrip() + "\n", encoding="utf-8")
    print(f"Generated tests: {output}")

if __name__ == "__main__":
    main()
