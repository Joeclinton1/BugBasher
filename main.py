import math
import random
from api3 import run
import unittest
import io
import sys
import re
import os
from example_test_cases import GraphTest

def extract_largest_code_block(text):
    code_blocks = extract_code_blocks(text)
    return max(code_blocks, key=len) if code_blocks else None

def extract_code_blocks(text):
    return re.findall(r'```(.*?)```', text, re.DOTALL)

def extract_code_and_text(text):

    code = extract_largest_code_block(text)
    # Remove code blocks from content
    text_without_code = re.sub(r'```(.*?)```', '', content, flags=re.DOTALL)
    
    return code, text_without_code.strip()

def add_bug_to_code(code):
    lines = code.split("\n")
    start_line = random.randint(0, len(lines)-3)
    end_line = start_line + 3
    code_extract = lines[start_line: end_line]
    prompt = f"Modify this code to purposefully add one bug. ```{code_extract}```"
    raw_output= run(prompt)
    buggy_code_extract = extract_largest_code_block(raw_output)
    if buggy_code_extract is None:
        prompt = f"Extract the code from this text: {raw_output}"
        buggy_code_extract = run(prompt)
    print("buggy_code_extract:", buggy_code_extract)
    buggy_code = "\n".join(lines[:start_line] + [buggy_code_extract] + lines[end_line:])
    return buggy_code, buggy_code_extract, code_extract

def run_tests_and_capture_output(test_module):
    captured_output = io.StringIO()
    
    # Load the tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromTestCase(test_module)

    # Run the tests
    test_runner = unittest.TextTestRunner(stream=captured_output)
    test_runner.run(test_suite)

    # Get the contents of StringIO buffer
    output = captured_output.getvalue()
    
    captured_output.close()
    return output

def extract_errors_from_test_output(test_output):
    # Regular expression to match lines with FAIL or ERROR
    error_pattern = re.compile(r'(FAIL|ERROR): .+')
    errors = error_pattern.findall(test_output)
    # Further process if needed, for now, just return the first two errors
    return len(errors), ' '.join(errors if len(errors) <2 else errors[:2])

def fix_bug(code, errors):
    if len(errors)>1000:
        errors = errors[:1000]
    prompt = f"""Here is my code file\n```\n{code}\n```
    When I run the test cases I get the following errors\n```\n{errors}\n```
    INSTRUCTION: tell me what the bug is given the test case outputs, then output code which fixes the bug
    """
    # print(prompt)
    return run(prompt)


def reflect_on_bug_fix(buggy_extract, predicted_fixed_extract,  predicted_solution, true_extract,):
    prompt = f"""here is an extract of buggy code\n```\n{buggy_extract}\n```
    I fixed it to get\n```\n{predicted_fixed_extract}\n```
    My reasoning behind this bug fix solution was:\n"\n{predicted_solution}\n"
    But the true code should've been:\n```\n{true_extract}\n```\n\n
    Tell me what was wrong and what was right with my solution focusing on the more general approach rather than the specifics.
    """
    return run(prompt)

def modify_guide(reflection, guide):
    prompt = f"""Reflection on solution:\n"\n{reflection}\n"\n 
    Update the following guide so that you can use it to avoid the same mistake in the future. Only include guidance relevant to this code
    \nGuide:\n"\n{guide}\n"
    """
    return run(prompt)



loss = math.inf
i = 0
min_loss = 0.001
code_file = "example_code.py"
test_cases = "example_test_cases.py"

while i < 10:
    print(f"i: {i}")
    # read code and guide file
    code_file = open(f"example_code.py", "r+")
    code = code_file.read()

    # Run test cases and extract errors
    test_output = run_tests_and_capture_output(GraphTest)
    # num_errors, errors = extract_errors_from_test_output(test_output)

    if not "FAILED" in test_output:
        print("Bashed all the bugs!")
        break

    # LLM, with the help of the guide, explains how it's going to fix the bug then fixes it
    # print(test_output)
    fixed_code = fix_bug(code, test_output)
    # print("help me")
    print(fixed_code)
    # code_file.seek(0)
    # code_file.write(fixed_code)
    # code_file.close()

    i += 1
