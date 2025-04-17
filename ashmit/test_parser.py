from parser_self import parser_util

def run_tests():
    tests = [
        ("cd /home/user", ["cd", "/home/user"]),
        ("ls -la", ["ls", "-la"]),
        ("echo 'hello world'", ["echo", "hello world"]),
        ("exit", ["exit"])
    ]

    for i, (input_cmd, expected) in enumerate(tests, 1):
        result = parser_util(input_cmd)
        if result == expected:
            print(f"Test {i} is Ok")
        else:
            print(f"Test {i} not Okay - Input: {input_cmd}\nExpected: {expected}\nGot: {result}")

if __name__ == "__main__":
    run_tests()
