import subprocess

def execute_git_commands():
    # Change this to the path of your git repository
    # Execute 'git fetch'
    subprocess.run(["git", "fetch"], check=True)

    # Execute 'git pull'
    subprocess.run(["git", "pull"], check=True)

if __name__ == "__main__":
    execute_git_commands()
