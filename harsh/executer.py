import os
import sys
import subprocess
import shutil
import threading
import time
import signal
import re
import fnmatch
import platform 
import datetime


from history import command_history
from chat import query_bash_ai

aliases = {}
background_jobs = []

# Signal Handlers
def handle_sigint(signal_number, frame):
    print("\nCtrl+C pressed: Interrupt received, but not exiting the shell.")

def handle_sigtstp(signal_number, frame):
    print("\nCtrl+Z pressed: Suspend signal received, but not suspending the shell.")

# Register signal handlers
if os.name == 'posix':
    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTSTP, handle_sigtstp)
elif os.name == 'nt':
    signal.signal(signal.SIGINT, handle_sigint)

def expand_variables_and_aliases(tokens):
    if not tokens:
        return []
    if tokens[0] in aliases:
        alias_expansion = aliases[tokens[0]].split()
        tokens = alias_expansion + tokens[1:]
    tokens = [os.path.expandvars(token) for token in tokens]
    return tokens

def cmd_grep(tokens, input_bytes=None):
    if len(tokens) < 2:
        return b"Usage: grep pattern [file]\n"
    
    pattern = tokens[1]
    lines = []
    
    if len(tokens) > 2:
        # Read from file
        try:
            with open(tokens[2], 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            return f"grep error: {e}\n".encode()
    else:
        # Use input_bytes from pipe if available
        if input_bytes:
            lines = input_bytes.decode(errors='ignore').splitlines()
        else:
            return b"grep error: no input or file provided\n"
    
    result = []
    for line in lines:
        if pattern in line:
            result.append(line)
    return ("\n".join(result) + "\n").encode()

def cmd_find(tokens):
    start_path = "."
    pattern = "*"
    
    if len(tokens) > 1:
        start_path = tokens[1]
    if len(tokens) > 2:
        pattern = tokens[2]
    
    matches = []
    try:
        for root, dirs, files in os.walk(start_path):
            for name in dirs + files:
                if fnmatch.fnmatch(name, pattern):
                    matches.append(os.path.join(root, name))
    except Exception as e:
        return str(e).encode()
    return ("\n".join(matches) + "\n").encode()

def cmd_df(tokens):
    try:
        # Use current drive or specified path
        path = tokens[1] if len(tokens) > 1 else "."
        total, used, free = shutil.disk_usage(path)
        
        def to_gb(n): return f"{n / (1024**3):.2f} GB"
        
        output = (
            f"Filesystem: {os.path.abspath(path)}\n"
            f"Total: {to_gb(total)}\n"
            f"Used: {to_gb(used)}\n"
            f"Free: {to_gb(free)}\n"
        )
        return output.encode()
    except Exception as e:
        return f"df error: {e}\n".encode()
    

def cmd_uptime(tokens):
    try:
        # Windows uptime via ctypes
        if os.name == 'nt':
            import ctypes
            import ctypes.wintypes
            
            class SYSTEM_TIME(ctypes.Structure):
                _fields_ = [('dwLowDateTime', ctypes.wintypes.DWORD),
                            ('dwHighDateTime', ctypes.wintypes.DWORD)]
            
            GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
            GetTickCount64.restype = ctypes.c_ulonglong
            millis = GetTickCount64()
            seconds = millis / 1000
        else:
            # On Unix, read from /proc/uptime
            with open("/proc/uptime") as f:
                seconds = float(f.readline().split()[0])
        
        days = int(seconds // (24*3600))
        seconds %= (24*3600)
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        
        return f"Uptime: {days}d {hours}h {minutes}m {seconds}s\n".encode()
    except Exception as e:
        return f"uptime error: {e}\n".encode()
    
    
def cmd_stat(tokens):
    if len(tokens) < 2:
        return b"Usage: stat filename\n"
    try:
        filepath = tokens[1]
        st = os.stat(filepath)
        size = st.st_size
        ctime = datetime.datetime.fromtimestamp(st.st_ctime)
        mtime = datetime.datetime.fromtimestamp(st.st_mtime)
        atime = datetime.datetime.fromtimestamp(st.st_atime)
        
        output = (
            f"  File: {filepath}\n"
            f"  Size: {size} bytes\n"
            f"  Created: {ctime}\n"
            f"  Modified: {mtime}\n"
            f"  Accessed: {atime}\n"
        )
        return output.encode()
    except Exception as e:
        return f"stat error: {e}\n".encode()
    

def cmd_uname(tokens):
    output = (
        f"System: {platform.system()}\n"
        f"Node Name: {platform.node()}\n"
        f"Release: {platform.release()}\n"
        f"Version: {platform.version()}\n"
        f"Machine: {platform.machine()}\n"
        f"Processor: {platform.processor()}\n"
    )
    return output.encode()

def cmd_tree(tokens):
    start_path = tokens[1] if len(tokens) > 1 else "."
    
    def walk_dir(path, prefix=""):
        lines = []
        try:
            entries = os.listdir(path)
        except Exception as e:
            return [f"tree error: {e}"]
        
        entries.sort()
        for i, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            lines.append(prefix + connector + entry)
            if os.path.isdir(full_path):
                extension = "    " if i == len(entries) - 1 else "│   "
                lines.extend(walk_dir(full_path, prefix + extension))
        return lines
    
    tree_lines = [start_path]
    tree_lines.extend(walk_dir(start_path))
    return ("\n".join(tree_lines) + "\n").encode()


def cmd_sort(tokens, input_bytes=None):
    lines = []
    if len(tokens) > 1:
        try:
            with open(tokens[1], 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            return f"sort error: {e}\n".encode()
    else:
        if input_bytes:
            lines = input_bytes.decode(errors='ignore').splitlines()
        else:
            return b"sort error: no input or file provided\n"
    
    lines.sort()
    return ("\n".join(line.rstrip('\n') for line in lines) + "\n").encode()




def run_command(cmd_tokens, input_bytes=None):
    if not cmd_tokens:
        return b""

    cmd = cmd_tokens[0]

    if cmd == "echo":
        return (" ".join(cmd_tokens[1:]) + "\n").encode()
    elif cmd == "pwd":
        return (os.getcwd() + "\n").encode()
    elif cmd == "whoami":
        try:
            return (os.getlogin() + "\n").encode()
        except:
            return os.environ.get("USERNAME", "unknown").encode()
    elif cmd == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
        return b""
    elif cmd == "ls":
        try:
            path = cmd_tokens[1] if len(cmd_tokens) > 1 else "."
            return ("\n".join(os.listdir(path)) + "\n").encode()
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
    elif cmd_tokens[0] == "kill":
        if len(cmd_tokens) < 2:
            print("Usage: kill <job_id>")
            return
        try:
            job_id = int(cmd_tokens[1])
        except:
            print("kill: job_id must be a number")
            return
        for job in background_jobs:
            if job["job_id"] == job_id:
                proc = job.get("process")
                if proc:
                    proc.terminate()
                    job["status"] = "Terminated"
                    print(f"Killed job [{job_id}]: {job['command']}")
                else:
                    print(f"Job [{job_id}] cannot be killed (no process handle).")
                return
        print(f"kill: no such job [{job_id}]")
        return
    elif cmd == "grep":
        return cmd_grep(cmd_tokens, input_bytes)
    elif cmd == "find":
        return cmd_find(cmd_tokens)
    elif cmd == "df":
        return cmd_df(cmd_tokens)
    elif cmd == "uptime":
        return cmd_uptime(cmd_tokens)
    elif cmd == "stat":
        return cmd_stat(cmd_tokens)
    elif cmd == "uname":
        return cmd_uname(cmd_tokens)
    elif cmd == "tree":
        return cmd_tree(cmd_tokens)
    elif cmd == "sort":
        return cmd_sort(cmd_tokens, input_bytes)
    
    elif cmd == "DocBot":
        if len(cmd_tokens) < 2:
            return b"bashai: missing question\n"
        question = " ".join(cmd_tokens[1:])
        result = query_bash_ai(question)

        GREEN = "\033[92m"
        RESET = "\033[0m"

        divider = GREEN + ("=*=" * 18) + "DocBot" + ("=*=" * 18) + RESET
        print(f"{divider}\nQuestion: {result['question']}\nAnswer: {result['explanation']}\nCode:\n{result['code']}\n{divider}")

        user_input = input(f"{GREEN}Do you want to run the above code? (y/n): {RESET}").strip().lower()
        if user_input == 'y':
            # Strip leading/trailing whitespaces
            raw_code = result['code'].strip()

            # Remove surrounding triple quotes
            if (raw_code.startswith('"""') and raw_code.endswith('"""')) or \
            (raw_code.startswith("'''") and raw_code.endswith("'''")):
                cleaned_code = raw_code[3:-3].strip()

            # Remove surrounding double quotes
            elif raw_code.startswith('"') and raw_code.endswith('"'):
                cleaned_code = raw_code[1:-1].strip()

            # Remove surrounding single quotes
            elif raw_code.startswith("'") and raw_code.endswith("'"):
                cleaned_code = raw_code[1:-1].strip()

            else:
                cleaned_code = raw_code  # No surrounding quotes

            # Tokenize the cleaned code
            new_tokens = cleaned_code.split()
            print(f"Executing code: {cleaned_code}")
            return run_command(new_tokens)
        else:
            return b"Skipped execution of suggested code.\n"



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

    if tokens[0] == "jobs":
        if background_jobs:
            for job in background_jobs:
                if job["status"].lower() == "running":
                    print(f"Job ID [{job['job_id']}]: {job['status']} - Command: {job['command']}")
        # If no running jobs found:
                else:
                    print("No running background jobs.")
        else:
            print("No background jobs.")
        return

    if tokens[0] == "history":
        for idx, cmd in enumerate(command_history, 1):
            print(f"{idx}: {cmd}")
        return

    if tokens[0] == "alias":
        if len(tokens) == 1:
            for name, val in aliases.items():
                print(f"alias {name}='{val}'")
        elif '=' in tokens[1]:
            name, val = tokens[1].split("=", 1)
            if len(tokens) > 2:
                val = " ".join([val] + tokens[2:])
            val = val.strip("'\"")
            aliases[name] = val
        else:
            print("Invalid alias format. Use: alias name='command'")
        return

    run_in_background = tokens[-1] == "&"
    if run_in_background:
        tokens = tokens[:-1]

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

    input_file = None
    output_file = None
    append = False
    new_tokens = []
    it = iter(tokens)
    for token in it:
        if token == "<":
            input_file = next(it, None)
        elif token == ">":
            output_file = next(it, None)
            append = False
        elif token == ">>":
            output_file = next(it, None)
            append = True
        else:
            new_tokens.append(token)
    tokens = new_tokens

    input_bytes = None
    if input_file:
        try:
            with open(input_file, "rb") as f:
                input_bytes = f.read()
        except Exception as e:
            print(f"Input redirection error: {e}")
            return

    def run_pipeline():
        try:
            if "|" in tokens:
                segments = " ".join(tokens).split("|")
                data = input_bytes
                for seg in segments:
                    cmd_tokens = expand_variables_and_aliases(seg.strip().split())
                    data = run_command(cmd_tokens, input_bytes=data)
            else:
                data = run_command(tokens, input_bytes=input_bytes)

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
        except Exception as e:
            print(f"Pipeline error: {e}")

    if run_in_background:
        thread = threading.Thread(target=run_pipeline)
        job_id = len(background_jobs) + 1
        background_jobs.append({
            "job_id": job_id,
            "command": " ".join(tokens),
            "thread": thread,
            "status": "Running"
        })
        thread.start()
    else:
        run_pipeline()
