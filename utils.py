import subprocess
import sys
from typing import List, Dict, Any

# Not yet safe for free input 
# run_code function is adapted from: https://github.com/zserio-streamlit/zserio-streamlit/blob/ec85e277b8ec40e8645d66f911ef00c6eb3feb62/interactive_zserio/python_runner.py#L38 
def run_code(code):
    try:
        completed_process = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True,
            timeout=5
        )

        # returns (code output, code errors)
        return (completed_process.stdout, completed_process.stderr)
    except subprocess.TimeoutExpired as e:
        raise Exception(f"{e.timeout}s timeout expired!")
    except Exception as e:
        raise Exception(e)