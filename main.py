import os  # for interacting with the operating system
import shlex  # for parsing command line arguments
import subprocess  # for executing shell commands

def run_shell():
    while True:
        try:
            cwd = os.getcwd()
            user_input = input(f"\033[92mBashAI ~ {cwd} > \033[0m")
            if not user_input.strip():
                continue
            args = shlex.split(user_input)

            # Handle exit command
            if args[0] == "exit":
                print("Exiting BashAI...")
                break

            # Handle cd command
            elif args[0] == "cd":
                try:
                    os.chdir(args[1])
                except IndexError:
                    print("BashAI: cd: missing argument")
                except FileNotFoundError:
                    print(f"BashAI: cd: no such file in directory: {args[1]}")

            # Run other commands
            else:
                subprocess.run(args, shell=True)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the BashAI.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_shell()