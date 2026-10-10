"""Run all four IR-SIM worlds in individual subprocesses."""
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys

WORLDS = ('world_easy.yaml', 'world_medium.yaml', 'world_hard.yaml', 'world_custom.yaml')


def extract_report(output):
    match = re.search(r'IR-SIM report:\s*(\{[^\n]*\})', output)
    if not match:
        raise ValueError('IR-SIM report not present in subprocess output')
    report = ast.literal_eval(match.group(1))
    if not isinstance(report, dict) or 'reached_goal' not in report or 'steps_taken' not in report:
        raise ValueError('Invalid IR-SIM report')
    return report


def run_world(world_file, timeout=180, headless=True):
    world_file = str(world_file)
    environment = os.environ.copy()
    if headless:
        environment['MPLBACKEND'] = 'Agg'
        environment['SCSE_HEADLESS'] = '1'
    try:
        p = subprocess.run([sys.executable, 'test_irsim_with_agent.py', world_file],
                           capture_output=True, text=True, timeout=timeout, env=environment)
        if p.returncode:
            raise RuntimeError((p.stderr or p.stdout)[-1400:])
        return {'world': world_file, **extract_report(p.stdout)}
    except (subprocess.TimeoutExpired, RuntimeError, ValueError) as exc:
        return {'world': world_file, 'reached_goal': False, 'collision_or_done': False,
                'steps_taken': 0, 'efficiency_status': 'failed', 'error': str(exc)}


def run_benchmark(world_dir='irsim_worlds', headless=True):
    results = [run_world(Path(world_dir) / w, headless=headless) for w in WORLDS]
    total = len(results)
    reached = sum(bool(r.get('reached_goal')) for r in results)
    efficient = sum(r.get('efficiency_status') == 'efficient' for r in results)
    inefficient = sum(r.get('efficiency_status') == 'acceptable_but_inefficient' for r in results)
    report = {'total_worlds': total, 'goals_reached': reached, 'success_rate': reached / total,
        'efficient_worlds': efficient, 'inefficient_success_worlds': inefficient,
        'failed_worlds': total - reached, 'efficiency_rate': efficient / total,
        'average_steps_taken': sum(r.get('steps_taken', 0) for r in results) / total,
        'results': results}
    Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/irsim_benchmark_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    print(json.dumps(run_benchmark(), indent=2))
