"""Single entry point for complete SCSE agent pipeline."""
import argparse
import importlib.util
import json
import logging
from pathlib import Path
import subprocess
import sys

from analyst_agent import run_analyst
from planner_agent import run_planner
from developer_agent import run_developer, run_developer_revision
from test_agent import run_test_agent
from runner import run_simulation
from reviewer_agent import run_reviewer_agent
from benchmark_irsim import run_benchmark
from reviewer_benchmark_agent import run_benchmark_reviewer_agent

LOGGER = logging.getLogger("scse")
ROOT = Path(__file__).resolve().parent


def save_json(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    LOGGER.info("Saved %s", path.relative_to(ROOT))


def save_text(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")
    LOGGER.info("Saved %s", path.relative_to(ROOT))


def load_navigation(path):
    spec = importlib.util.spec_from_file_location("scse_navigation_latest", ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decide_next_move


def evaluate(code_path, label, use_llm_reviews=False, with_benchmark=True):
    LOGGER.info("Evaluate %s", label)
    requirements = json.loads((ROOT / "artifacts/requirements.json").read_text(encoding="utf-8"))
    plan = json.loads((ROOT / "artifacts/plan.json").read_text(encoding="utf-8"))
    code = (ROOT / code_path).read_text(encoding="utf-8")
    tests = run_test_agent(requirements, plan, code)
    save_text("generated/test_navigation_logic.py", tests)
    LOGGER.info("Test Agent created pytest cases")
    run_tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "generated/test_navigation_logic.py"], cwd=ROOT, capture_output=True, text=True)
    LOGGER.info("Pytest (%s) exit=%s: %s %s", label, run_tests.returncode, run_tests.stdout[-2500:], run_tests.stderr[-1000:])
    # Never discard failed tests: reviewers must see them.
    simulation = run_simulation(load_navigation(code_path))
    simulation["pytest_passed"] = run_tests.returncode == 0
    simulation["pytest_summary"] = (run_tests.stdout + run_tests.stderr)[-1800:]
    save_json(f"artifacts/simulation_report{label}.json", simulation)
    from developer_agent import ollama_llm
    review = run_reviewer_agent(simulation, llm=ollama_llm if use_llm_reviews else None)
    if run_tests.returncode:
        review["needs_revision"] = True
        review["issue"] += "; generated pytest tests failed"
    save_json(f"artifacts/simulation_review{label}.json", review)
    benchmark = None
    benchmark_review = None
    if with_benchmark:
        benchmark = run_benchmark()
        save_json(f"artifacts/irsim_benchmark_report{label}.json", benchmark)
        benchmark_review = run_benchmark_reviewer_agent(benchmark, llm=ollama_llm if use_llm_reviews else None)
        save_json(f"artifacts/irsim_benchmark_review{label}.json", benchmark_review)
    return review, benchmark, benchmark_review


def main(argv=None):
    parser = argparse.ArgumentParser(description="SCSE group project complete pipeline")
    parser.add_argument("--skip-benchmark", action="store_true", help="Only test discrete scenarios")
    parser.add_argument("--skip-revision", action="store_true", help="Do not request revised code")
    parser.add_argument("--llm-reviews", action="store_true", help="Use Qwen for explanatory reviews")
    args = parser.parse_args(argv)
    (ROOT / "artifacts").mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler(ROOT / "trace.log", encoding="utf-8", mode="w"), logging.StreamHandler(sys.stdout)], force=True)
    try:
        brief = (ROOT / "brief.txt").read_text(encoding="utf-8")
        LOGGER.info("Loaded brief.txt")
        requirements = run_analyst(brief)
        save_json("artifacts/requirements.json", requirements)
        LOGGER.info("Analyst Agent completed")
        plan = run_planner(requirements)
        save_json("artifacts/plan.json", plan)
        LOGGER.info("Planner Agent completed")
        code = run_developer(plan)
        save_text("generated/navigation_logic.py", code)
        LOGGER.info("Developer Agent completed")
        review, benchmark, benchmark_review = evaluate("generated/navigation_logic.py", "", args.llm_reviews, not args.skip_benchmark)
        needs_revision = review["needs_revision"] or (benchmark_review is not None and benchmark_review["needs_revision"])
        if needs_revision and not args.skip_revision:
            LOGGER.info("Revision required: Developer Agent revising code")
            revised = run_developer_revision(code, {"simulation_review":review, "benchmark_review":benchmark_review}, benchmark, requirements, plan)
            # Save the original; only replace active module after a verified revised artifact exists.
            revised_code = (ROOT / revised).read_text(encoding="utf-8")
            save_text("generated/navigation_logic_original.py", code)
            save_text("generated/navigation_logic.py", revised_code)
            LOGGER.info("Revised navigation code activated; rerunning tests and benchmark")
            evaluate("generated/navigation_logic.py", "_revised", args.llm_reviews, not args.skip_benchmark)
        else:
            LOGGER.info("No revision run (not needed or explicitly skipped)")
        LOGGER.info("Pipeline finished successfully")
    except Exception:
        LOGGER.exception("Pipeline failed")
        raise

if __name__ == "__main__":
    main()
