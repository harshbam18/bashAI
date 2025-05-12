# parser.py

import shlex

def parse_command(input_line):

    try:
        tokens = shlex.split(input_line)
    except ValueError as e:
        print(f"Parsing error: {e}")
        return None

    pipeline = []
    current_cmd = []

    input_file = None
    output_file = None
    append_mode = False

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "|":
            if current_cmd:
                pipeline.append(current_cmd)
                current_cmd = []
        elif token == "<":
            i += 1
            if i < len(tokens):
                input_file = tokens[i]
        elif token == ">":
            i += 1
            if i < len(tokens):
                output_file = tokens[i]
                append_mode = False
        elif token == ">>":
            i += 1
            if i < len(tokens):
                output_file = tokens[i]
                append_mode = True
        else:
            current_cmd.append(token)
        i += 1

    if current_cmd:
        pipeline.append(current_cmd)

    return {
        "pipeline": pipeline,
        "input": input_file,
        "output": output_file,
        "append": append_mode
    }
