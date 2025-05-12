import os
import sys
import subprocess
import shutil
import threading
import time  
#global alias and job list
aliases = {}
background_jobs = []

def expand_variables_and_aliases(tokens):
    if not tokens:
        return []

    if tokens[0] in aliases:
        alias_expansion = aliases[tokens[0]].split()
        tokens = alias_expansion + tokens[1:]

    tokens = [os.path.expandvars(token) for token in tokens]
    return tokens

def run_command(cmd_tokens, input_bytes=None):
    if not cmd_tokens:
        return b""

    cmd = cmd_tokens[0]

    if cmd == "echo":
        out = " ".join(cmd_tokens[1:]) + "\n"
        return out.encode()

    elif cmd == "pwd":
        return (os.getcwd() + "\n").encode()

    elif cmd == "whoami":
        return (os.getlogin() + "\n").encode()

    elif cmd == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
        return b""

    elif cmd == "ls":
        try:
            path = cmd_tokens[1] if len(cmd_tokens) > 1 else "."
            entries = os.listdir(path)
            return ("\n".join(entries) + "\n").encode()
        except Exception as e:
            return (f"ls error: {e}\n").encode()

    elif cmd == "dir":
        try:
            args = cmd_tokens[1:] if len(cmd_tokens) > 1 else []
            result = subprocess.run(["cmd", "/c", "dir"] + args, capture_output=True, text=True)
            return result.stdout.encode()
        except Exception as e:
            return f"dir error: {e}\n".encode()

    elif cmd == "cat":
        if len(cmd_tokens) < 2:
            return input_bytes or b""
        try:
            return open(cmd_tokens[1], "rb").read()
        except Exception as e:
            return f"cat error: {e}\n".encode()

    elif cmd == "touch":
        try:
            open(cmd_tokens[1], "a").close()
        except Exception as e:
            return f"touch error: {e}\n".encode()
        return b""

    elif cmd == "mkdir":
        try:
            os.mkdir(cmd_tokens[1])
        except Exception as e:
            return f"mkdir error: {e}\n".encode()
        return b""

    elif cmd == "rmdir":
        try:
            os.rmdir(cmd_tokens[1])
        except Exception as e:
            return f"rmdir error: {e}\n".encode()
        return b""

    elif cmd == "cp":
        try:
            if len(cmd_tokens) < 3:
                return b"cp: missing source or destination\n"
            shutil.copy(cmd_tokens[1], cmd_tokens[2])
        except Exception as e:
            return f"cp error: {e}\n".encode()
        return b""

    elif cmd == "mv":
        try:
            if len(cmd_tokens) < 3:
                return b"mv: missing source or destination\n"
            shutil.move(cmd_tokens[1], cmd_tokens[2])
        except Exception as e:
            return f"mv error: {e}\n".encode()
        return b""

    elif cmd == "rm":
        try:
            os.remove(cmd_tokens[1])
        except Exception as e:
            return f"rm error: {e}\n".encode()
        return b""
    
    elif cmd == "sleep":
        try:
            seconds = int(cmd_tokens[1]) if len(cmd_tokens) > 1 else 1
            time.sleep(seconds)
            return f"Slept for {seconds} seconds.\n".encode()
        except Exception as e:
            return f"sleep error: {e}\n".encode()

    elif cmd == "countdown":
        try:
            start = int(cmd_tokens[1]) if len(cmd_tokens) > 1 else 5
            result = ""
            for i in range(start, 0, -1):
                result += f"{i}...\n"
                time.sleep(1)
            result += "Go!\n"
            return result.encode()
        except Exception as e:
            return f"countdown error: {e}\n".encode()

    elif cmd == "repeat":
        try:
            word = cmd_tokens[1] if len(cmd_tokens) > 1 else "hello"
            count = int(cmd_tokens[2]) if len(cmd_tokens) > 2 else 5
            result = ""
            for _ in range(count):
                result += word + "\n"
                time.sleep(1)
            return result.encode()
        except Exception as e:
            return f"repeat error: {e}\n".encode()

    try:
        proc = subprocess.run(cmd_tokens, input=input_bytes, capture_output=True)
        return proc.stdout + proc.stderr
    except FileNotFoundError:
        return f"{cmd}: command not found\n".encode()
    except Exception as e:
        return f"Error running {cmd}: {e}\n".encode()

def execute_command(tokens):
    if not tokens:
        return

    if tokens[0] == "alias":
        if len(tokens) == 1:
            for name, val in aliases.items():
                print(f"alias {name}='{val}'")
        elif '=' in tokens[1]:
            parts = tokens[1].split("=", 1)
            name = parts[0]
            val = parts[1].strip("'\"")
            aliases[name] = val
        else:
            print("Invalid alias format. Use: alias name='command'")
        return

    # Check for background execution
    run_in_background = tokens[-1] == "&"
    if run_in_background:
        tokens = tokens[:-1]  # Remove &

    tokens = expand_variables_and_aliases(tokens)

    if tokens[0] == "exit":
        print("Exiting shell...")
        sys.exit(0)
    elif tokens[0] == "cd":
        try:
            os.chdir(tokens[1] if len(tokens) > 1 else os.path.expanduser("~"))
        except Exception as e:
            print(f"cd error: {e}")
        return

    # Handle redirection: <, >, >>
    input_file = None
    output_file = None
    append = False
    new_tokens = []
    it = iter(tokens)
    for token in it:
        if token == "<":
            try:
                input_file = next(it)
            except StopIteration:
                print("Syntax error: expected filename after '<'")
                return
        elif token == ">":
            try:
                output_file = next(it)
                append = False
            except StopIteration:
                print("Syntax error: expected filename after '>'")
                return
        elif token == ">>":
            try:
                output_file = next(it)
                append = True
            except StopIteration:
                print("Syntax error: expected filename after '>>'")
                return
        else:
            new_tokens.append(token)
    tokens = new_tokens

    # Input redirection
    input_bytes = None
    if input_file:
        try:
            with open(input_file, "rb") as f:
                input_bytes = f.read()
        except Exception as e:
            print(f"Input redirection error: {e}")
            return

    # Handle piping
    def run_pipeline():
        if "|" in tokens:
            segments = " ".join(tokens).split("|")
            data = input_bytes
            for seg in segments:
                cmd_tokens = seg.strip().split()
                cmd_tokens = expand_variables_and_aliases(cmd_tokens)
                data = run_command(cmd_tokens, input_bytes=data)
            if output_file:
                try:
                    mode = "ab" if append else "wb"
                    with open(output_file, mode) as f:
                        f.write(data)
                except Exception as e:
                    print(f"Output redirection error: {e}")
            else:
                if data:
                    sys.stdout.write(data.decode())
        else:
            out = run_command(tokens, input_bytes=input_bytes)
            if output_file:
                try:
                    mode = "ab" if append else "wb"
                    with open(output_file, mode) as f:
                        f.write(out)
                except Exception as e:
                    print(f"Output redirection error: {e}")
            else:
                if out:
                    sys.stdout.write(out.decode())

    if run_in_background:
        thread = threading.Thread(target=run_pipeline)
        thread.start()
    else:
        run_pipeline()
