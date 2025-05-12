# test_parser.py

from parser import parse_command

def test_parse():
    tests = [
        {
            "input": 'ls -la /home/user',
            "expected": {
                "pipeline": [["ls", "-la", "/home/user"]],
                "input": None,
                "output": None,
                "append": False
            }
        },
        {
            "input": 'cat input.txt | grep "error" > output.txt',
            "expected": {
                "pipeline": [["cat", "input.txt"], ["grep", "error"]],
                "input": None,
                "output": "output.txt",
                "append": False
            }
        },
        {
            "input": 'sort < unsorted.txt >> sorted.txt',
            "expected": {
                "pipeline": [["sort"]],
                "input": "unsorted.txt",
                "output": "sorted.txt",
                "append": True
            }
        },
        {
            "input": 'echo "Hello World"',
            "expected": {
                "pipeline": [["echo", "Hello World"]],
                "input": None,
                "output": None,
                "append": False
            }
        }
    ]

    for i, test in enumerate(tests):
        result = parse_command(test["input"])
        if result == test["expected"]:
            print(f"Test {i + 1} ✅")
        else:
            print(f"Test {i + 1} ❌")
            print(f"Input: {test['input']}")
            print(f"Expected: {test['expected']}")
            print(f"Got:      {result}")

if __name__ == "__main__":
    test_parse()
