import subprocess
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--files', default='.')
args = parser.parse_args()

list_files = args.files
def update_git_repository(repository_path, branch_name, list_files ='.'):
	try:
		# Change directory to the Git repository location
		# os.chdir(repository_path)

		# Pull the latest changes from the remote repository
		subprocess.run(['git', 'pull', 'origin', branch_name], check=True)
		print("First pull ")
		# Optionally, commit and push your local changes
		subprocess.run(['git', 'add', list_files], check=True)
		subprocess.run(['git', 'commit', '-m', 'Automated commit'], check=True)
		subprocess.run(['git', 'push', 'origin', branch_name], check=True)

		print("Local repository updated successfully.")

	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")
	except Exception as e:
		print(f"An error occurred: {e}")

if __name__ == "__main__":
	# Set the path to your local Git repository and branch name
	repository_path = ""
	branch_name = "main"  # Replace with your branch name

	update_git_repository(repository_path, branch_name, list_files ='.')
