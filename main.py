import os  
import shlex  
import subprocess 

def run_shell():
    while True:
        try:
            cwd = os.getcwd()
            user_input = input(f"\033[92mBashAI ~ {cwd} > \033[0m")
            if not user_input.strip():
                continue
            args = shlex.split(user_input)

            if args[0] == "exit":
                print("Exiting BashAI...")
                break

            elif args[0] == "cd":
                try:
                    os.chdir(args[1])
                except IndexError:
                    print("BashAI: cd: missing argument")
                except FileNotFoundError:
                    print(f"BashAI: cd: no such file in directory: {args[1]}")

            else:
                subprocess.run(args, shell=True)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the BashAI.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_shell()