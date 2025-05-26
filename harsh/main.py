import signal
import os
import readline
import glob
from parser_self import parser_util
from executer import execute_command, background_jobs, aliases
from history import command_history

import signal
from executer import execute_command

BUILTIN_COMMANDS = [
    "cd", "pwd", "exit", "clear", "mkdir", "rmdir", "echo", "ls", "dir",
    "touch", "cp", "mv", "rm", "whoami", "jobs", "alias", "DocBot",
    "grep", "find", "df", "uptime", "stat", "uname", "tree", "sort", "history", "sleep", "countdown", "repeat", 
]


def complete(text, state):
    buffer = readline.get_line_buffer().split()
    if len(buffer) <= 1:
        options = list(aliases.keys()) + BUILTIN_COMMANDS
    else:
        dirname, rest = os.path.split(text)
        dirname = dirname or "."
        try:
            entries = os.listdir(dirname)
        except FileNotFoundError:
            entries = []
        options = [os.path.join(dirname, e) for e in entries if e.startswith(rest)]
    matches = [o for o in options if o.startswith(text)]
    return matches[state] if state < len(matches) else None

readline.parse_and_bind("tab: complete")
readline.set_completer_delims(" \t\n;")
readline.set_completer(complete)

# Install signal handlers again (if needed, especially on Windows)
signal.signal(signal.SIGINT, signal.default_int_handler)

def shell_loop():
    while True:
        try:
            GREEN = "\033[92m"
            RESET = "\033[0m"

            user_input = input(f"{GREEN}DocBot> {RESET}").strip()

            if not user_input:
                continue
            command_history.append(user_input) 
            tokens = user_input.split()
            execute_command(tokens)
        except KeyboardInterrupt:
            print("\nCtrl+C pressed: Shell continues...")
        except EOFError:
            print("\nExiting shell (EOF).")
            break

shell_loop()
