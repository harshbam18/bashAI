import shlex

def parser_util(input_line):
    try:
        return shlex.split(input_line)
    except ValueError as e:
        print("There is a Parsing Error : {e}")
        return []