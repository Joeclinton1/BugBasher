import math
import random
from api import run
import unittest
import io
import sys
import re
import os
import importlib
from update_code import update_code
import example_test_cases

def extract_largest_code_block(text):
    code_blocks = extract_code_blocks(text)
    return max(code_blocks, key=len) if code_blocks else None

def extract_code_blocks(text):
    # This pattern matches code blocks that start with ``` and may or may not end with ```
    # It captures the potential language specifier and the code
    code_blocks = re.findall(r'```(\w+)?\s*(.*?)(```|$)', text, re.DOTALL)
    languages = {'python', 'javascript', 'java', 'c', 'cpp', 'csharp', 'ruby', 'go', 'php'}
    return [code if (language.lower() in languages or not language) else language + code
            for language, code, end in code_blocks]

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
    INSTRUCTION: tell me what the bug is, given the test case outputs
    """
    bug_fix_explanation = run(prompt)
    print("bug fix explanation: ", bug_fix_explanation, '\n')
    prompt = f"""Here is my code file\n```\n{code}\n```
    this has a bug in it described below:\n
    {bug_fix_explanation}\n
    Output code which fixes the lines with bugs. Your code should match my code files indentation format. Surround your code in ```
    """
    for _ in range(3):
        fixed_code_extract = run(prompt)
        print("fixed code extract (before): ", fixed_code_extract)
        if extract_code_blocks(fixed_code_extract):
            fixed_code_extract = extract_code_blocks(fixed_code_extract)[0]
            # print("fixed code extract: ", fixed_code_extract,"\n")
            fixed_code = update_code(code, fixed_code_extract)
            return fixed_code
        else:
            print("failed to extract code from bug fix. Retrying")
    return None

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

# read code and guide file
with open(code_file, "r") as f:
    code = f.read()

# Run test cases and extract errors
test_output = run_tests_and_capture_output(example_test_cases.GraphTest)
# num_errors, errors = extract_errors_from_test_output(test_output)

if not "FAILED" in test_output:
    print("Code has no bugs")
    exit()

while i < 3:
    print(f"i: {i}")

    fixed_code = fix_bug(code, test_output)
    if fixed_code is not None:
        with open(code_file, "w") as f:
            f.write(fixed_code)

        importlib.reload(sys.modules['example_code'])
        importlib.reload(example_test_cases)
        test_output_new = run_tests_and_capture_output(example_test_cases.GraphTest)
        print(test_output_new)
        if not "FAILED" in test_output_new:
            print("Bugs have been Bashed!")
            break
    else:
        print("Failed to return any fixed code. Lets try this again")
    
    i += 1
else:
    print("Failed to bash the bugs")
    with open(code_file, "w") as f:
            f.write(code)
