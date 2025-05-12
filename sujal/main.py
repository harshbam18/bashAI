import signal
import os
from parser_self import parser_util
from executer import execute_command, background_jobs
from history import command_history

import signal
from executer import execute_command

# Install signal handlers again (if needed, especially on Windows)
signal.signal(signal.SIGINT, signal.default_int_handler)

def shell_loop():
    while True:
        try:
            user_input = input("bashAI> ").strip()
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
