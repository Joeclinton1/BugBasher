import numpy as np

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def ensure_correct_indents(code_line, tab_count, indent_char):
    # Replace existing leading whitespace with the specified number of tab spaces
    return indent_char * tab_count + code_line.lstrip()

def count_indentation(line):
    return int(sum(1 for c in line[:len(line) - len(line.lstrip())]))

def detect_indentation_character(code):
    # Find the first indented line and check the first character
    lines = code.split('\n')
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line and line != stripped_line:
            return '\t' if line[0] == '\t' else ' '
    return None

def calculate_actions(buggy_code, code_extract, threshold):
    actions = []
    buggy_code_lines = buggy_code.split('\n')
    extract_lines = code_extract.split('\n')
    used_indices = set()
    last_used_index = -1  # Track the last used index to ensure we don't go backwards

    for extract_line in extract_lines:
        line_distances = [levenshtein_distance(extract_line, buggy_line) for buggy_line in buggy_code_lines]
        # Filter out the indices that are less than the last used index to maintain order
        line_distances = [(dist, idx) if idx > last_used_index else (float('inf'), idx) for idx, dist in enumerate(line_distances)]
        dist, line_idx = min(line_distances)
        
        if dist <= threshold and not(not extract_line.strip() and line_idx>last_used_index+1):
            actions.append(("replace", line_idx, extract_line))
            used_indices.add(line_idx)
            last_used_index = line_idx  # Update the last used index
        else:
            actions.append(("insert", None, extract_line))  # The insert location is after the last replacement

    return actions

def apply_actions(buggy_code, actions):
    buggy_code_lines = buggy_code.split('\n')
    updated_code = buggy_code_lines.copy()  # Start with a copy of the buggy code
    current_line = 0
    offset = 0  # This will track the index offset caused by insertions
    indent_char = detect_indentation_character(buggy_code)
    # Loop through actions
    for i, (action, line_idx, extract_line) in enumerate(actions):
        if action == "replace":
            # Calculate the current index in the updated code
            current_line = line_idx + offset
            # Replace the line at the current index with line from extract
            indent_tab_num = count_indentation(updated_code[current_line])
            updated_code[current_line] = ensure_correct_indents(extract_line,indent_tab_num, indent_char)

            # get next replace idx
            next_replace_idx = None
            j = i+1
            while j<len(actions):
                if actions[j][0] == "replace":
                    next_replace_idx = actions[j][1]
                    break
                j+=1

            # If two lines are more than 1 line apart in their replacement, delete all lines in between
            if next_replace_idx is not None and (next_replace_idx - line_idx >1):  # Check if there is a next replace
                del updated_code[current_line + 1: current_line + (next_replace_idx - line_idx)]
                offset -= (next_replace_idx- line_idx - 1)

        elif action == "insert":
            # Insert the extract line at the current index
            updated_code.insert(current_line+1,extract_line)
            current_line +=1
            offset += 1  # Increase the offset due to the insertion

    return '\n'.join(updated_code)

def update_code(buggy_code, fixed_code_extract):
    actions = calculate_actions(buggy_code, fixed_code_extract, threshold=10)
    updated_code = apply_actions(buggy_code, actions)
    return updated_code

if __name__ == '__main__':
    # New Buggy code and Fixed code provided
    buggy_code = """
    class Graph:
        def add_node(self, node):
            if node not in self.adjacency_list:
                self.adjacency_list[node] = []

        def add_edge(self, src, dest, weight=-1):
            if src not in self.adjacency_list:
                self.add_node(src)
            if dest not in self.adjacency_list:
                self.add_node(dest)
            self.adjacency_list[src].append((dest, weight))
    """

    fixed_code = """
    class Graph:
        
        def add_edge(self, src, dest, weight=-1):
                if src not in self.adjacency_list:
                    self.add_node(src)
                if dest not in self.adjacency_list:
                    self.add_node(dest)
                self.adjacency_list[src].append((dest, weight))
    """

    updated_code = update_code(buggy_code, fixed_code)
    print(updated_code)