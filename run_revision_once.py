import json
from pathlib import Path
from developer_agent import run_developer_revision

ROOT = Path(__file__).resolve().parent

def load_json(filename):
    return json.loads(
        (ROOT / filename).read_text(encoding="utf-8")
    )

def main():
    original_code = (
        ROOT / "generated/navigation_logic_original.py"
    ).read_text(encoding="utf-8")

    requirements = load_json("artifacts/requirements.json")
    plan = load_json("artifacts/plan.json")
    benchmark = load_json("artifacts/irsim_benchmark_report.json")
    simulation_review = load_json("artifacts/simulation_review.json")
    benchmark_review = load_json("artifacts/irsim_benchmark_review.json")

    review_notes = {
        "simulation_review": simulation_review,
        "benchmark_review": benchmark_review,
        "additional_instruction": (
            "Generate an independently revised navigation implementation. "
            "Preserve safety, goal completion, and action requirements. "
            "Improve code readability and defensive handling. "
            "Do not invent failures in the original implementation."
        )
    }

    result = run_developer_revision(
        original_navigation_code=original_code,
        review_notes=review_notes,
        benchmark_report=benchmark,
        requirements=requirements,
        plan=plan,
        output_path="generated/navigation_logic_revised.py"
    )

    print("Revised navigation logic generated:", result)

if __name__ == "__main__":
    main()
