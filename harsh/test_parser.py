from parser_self import parser_util

def run_tests():
    tests = [
        ("cd /home/user", ["cd", "/home/user"]),
        ("ls -la", ["ls", "-la"]),
        ("pwd", ["pwd"]),
        ("clear", ["clear"]),
        ("mkdir testdir", ["mkdir", "testdir"]),
        ("rmdir testdir", ["rmdir", "testdir"]),
        ("echo Hello World", ["echo", "Hello", "World"]),
        ("cat file1.txt file2.txt", ["cat", "file1.txt", "file2.txt"]),
        ("exit", ["exit"]),
        ("echo 'Hello World'", ["echo", "Hello World"]),
        ("echo \"Quoted String Test\"", ["echo", "Quoted String Test"]),
        ("ls > output.txt", ["ls", ">", "output.txt"]),
        ("echo Hello >> log.txt", ["echo", "Hello", ">>", "log.txt"]),
        ("cat < input.txt", ["cat", "<", "input.txt"]),
        ("echo 'This is > not redirection'", ["echo", "This is > not redirection"]),
        ("echo \"Use < and > safely\"", ["echo", "Use < and > safely"]),
        ("export NAME=World", ["export", "NAME=World"]),

        ("alias ll='ls -la'", ["alias", "ll=ls -la"]),
        ("alias hi='echo Hello $USER'", ["alias", "hi=echo Hello $USER"]),

        ("echo $HOME", ["echo", "$HOME"]),
        ("echo $PATH", ["echo", "$PATH"])
    ]

    passed = 0
    for i, (input_cmd, expected) in enumerate(tests, 1):
        result = parser_util(input_cmd)
        if result == expected:
            print(f"✅ Test {i} Passed")
            passed += 1
        else:
            print(f"❌ Test {i} Failed\nInput:    {input_cmd}\nExpected: {expected}\nGot:      {result}\n")

    print(f"\n{passed}/{len(tests)} tests passed.")

if __name__ == "__main__":
    run_tests()
