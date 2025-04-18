import os
import subprocess
import sys
import shutil

aliases = {} 

def expand_variables_and_aliases(tokens):
    if not tokens:
        return []

    if tokens[0] in aliases:
        alias_expansion = aliases[tokens[0]].split()
        tokens = alias_expansion + tokens[1:]

    tokens = [os.path.expandvars(token) for token in tokens]
    return tokens

def execute_command(tokens):
    if not tokens:
        return

    if '>' in tokens or '>>' in tokens or '<' in tokens:
        handle_redirection(tokens)
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
    elif command == "pwd":
        print(os.getcwd())

    elif command == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
        
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

    elif command == "rmdir":
        try:
            if len(tokens) < 2:
                print("rmdir: missing directory name")
            else:
                os.rmdir(tokens[1])
        except FileNotFoundError:
            print(f"rmdir: '{tokens[1]}' not found")
        except OSError:
            print(f"rmdir: '{tokens[1]}' is not empty or not a directory")
        except Exception as e:
            print(f"rmdir error: {e}")

    elif command == "echo":
        output = " ".join(tokens[1:])
        print(output)
    elif command == "ls":
        args = tokens[1:]
        try:
            subprocess.run(["ls"] + args)
        except Exception as e:
            print(f"ls error: {e}")

    elif command == "cat":
        if len(tokens) < 2:
            print("cat: missing filename")
        else:
            for file in tokens[1:]:
                try:
                    with open(file, 'r') as f:
                        print(f.read(), end="")
                except FileNotFoundError:
                    print(f"cat: {file}: No such file")
                except Exception as e:
                    print(f"cat: error reading {file}: {e}")
    elif command == "dir":
        try:
            args = tokens[1:] if len(tokens) > 1 else []
            if os.name == 'nt': 
                subprocess.run(["cmd", "/c", "dir"] + args)
            else:  
                subprocess.run(["ls", "-l"] + args)
        except Exception as e:
            print(f"Error running dir: {e}")
            
    elif command == "touch":
        try:
            if len(tokens) < 2:
                print("touch: missing file name")
            else:
                with open(tokens[1], 'a'):
                    os.utime(tokens[1], None)  
        except Exception as e:
            print(f"touch error: {e}")
            
    elif command == "cp":
        try:
            if len(tokens) < 3:
                print("cp: missing source or destination")
            else:
                shutil.copy(tokens[1], tokens[2]) 
        except FileNotFoundError:
            print(f"cp: source file not found: {tokens[1]}")
        except Exception as e:
            print(f"cp error: {e}")

    elif command == "mv":
        try:
            if len(tokens) < 3:
                print("mv: missing source or destination")
            else:
                shutil.move(tokens[1], tokens[2])  
        except FileNotFoundError:
            print(f"mv: source file not found: {tokens[1]}")
        except Exception as e:
            print(f"mv error: {e}")

    elif command == "rm":
        try:
            if len(tokens) < 2:
                print("rm: missing file name")
            else:
                os.remove(tokens[1]) 
        except FileNotFoundError:
            print(f"rm: no such file: {tokens[1]}")
        except Exception as e:
            print(f"rm error: {e}")

    elif command == "whoami":
        print(os.getlogin())
               

    else:
        try:
            subprocess.run(tokens)
        except FileNotFoundError:
            print(f"{command}: command not found")
        except Exception as e:
            print(f"Error running command: {e}")


def handle_redirection(tokens):
    if '>' in tokens:
        op_index = tokens.index('>')
        mode = 'w'
    elif '>>' in tokens:
        op_index = tokens.index('>>')
        mode = 'a'
    elif '<' in tokens:
        op_index = tokens.index('<')
        mode = 'r'
    else:
        print("Unsupported redirection syntax")
        return

    cmd = tokens[:op_index]
    file = tokens[op_index + 1] if len(tokens) > op_index + 1 else None

    if not file:
        print("Redirection: missing filename")
        return

    try:
        if mode == 'r':
            with open(file, 'r') as f:
                subprocess.run(cmd, stdin=f)
        else:
            with open(file, mode) as f:
                subprocess.run(cmd, stdout=f)
    except FileNotFoundError:
        print(f"Redirection: file '{file}' not found")
    except Exception as e:
        print(f"Redirection error: {e}")
