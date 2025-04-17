from parser_self import parser_util
from executer import execute_command

def shell_loop():
    while True:
        try:
            user_input = input("bashAI> ")
            tokens =  parser_util(user_input)
            execute_command(tokens)
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the shell.")

if __name__ == "__main__":
    shell_loop()
