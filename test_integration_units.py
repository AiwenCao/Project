import json
from pathlib import Path
from runner import create_scenarios, run_simulation
from reviewer_agent import validate_review, run_reviewer_agent
from reviewer_benchmark_agent import build_deterministic_review, validate_benchmark_review
from benchmark_irsim import extract_report
from test_agent import validate_test_code
from generated.navigation_logic import decide_next_move


def test_all_discrete_states():
    report = run_simulation(decide_next_move)
    assert report["total_scenarios"] == 64
    assert report["failed_scenarios"] == 0


def test_simulation_reviewer():
    review = run_reviewer_agent(run_simulation(decide_next_move))
    assert validate_review(review)["needs_revision"] is False


def test_benchmark_reviewer_detects_failure():
    report = {"total_worlds": 4, "success_rate": 0.75, "efficiency_rate": 0.5,
              "inefficient_success_worlds": 1,
              "results": [{"reached_goal": False, "collision_or_done": True}]}
    review = build_deterministic_review(report)
    assert review["needs_revision"] is True
    assert review["safety_passed"] is False
    assert validate_benchmark_review(review) == review


def test_report_parsing():
    report = extract_report("IR-SIM report:\n{'reached_goal': True, 'steps_taken': 42}")
    assert report["steps_taken"] == 42


def test_generated_test_validation():
    code = "from generated.navigation_logic import decide_next_move\ndef test_move():\n    assert decide_next_move({}) == 'STOP'\n"
    assert validate_test_code(code) == code
