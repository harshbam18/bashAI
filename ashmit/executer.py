import os
import subprocess
import sys

def execute_command(tokens):
    if not tokens:
        return

    command = tokens[0]

    if command == "exit":
        print("Exiting shell...")
        sys.exit(0)

    elif command == "cd":
        try:
            target_dir = tokens[1] if len(tokens) > 1 else os.path.expanduser("~")
            os.chdir(target_dir)
        except IndexError:
            print("cd: missing argument")
        except FileNotFoundError:
            print(f"cd: no such file or directory: {tokens[1]}")
        except Exception as e:
            print(f"cd error: {e}")

    elif command == "dir":
        try:
            args = tokens[1:] if len(tokens) > 1 else []
            subprocess.run(["cmd", "/c", "dir"] + args)
        except Exception as e:
            print(f"Error running dir: {e}")

    elif command == "mkdir":
        try:
            if len(tokens) < 2:
                print("mkdir: missing directory name")
            else:
                os.mkdir(tokens[1])
        except FileExistsError:
            print(f"mkdir: '{tokens[1]}' already exists")
        except Exception as e:
            print(f"mkdir error: {e}")

    else:
        try:
            subprocess.run(tokens)
        except FileNotFoundError:
            print(f"{command}: command not found")
        except Exception as e:
            print(f"Error running command: {e}")
