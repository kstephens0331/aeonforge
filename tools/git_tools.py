import git
import os

def git_commit(repo_path: str, commit_message: str) -> str:
    """
    Stages all changes and creates a commit in a local Git repository.

    Args:
        repo_path (str): The file system path to the local git repository.
        commit_message (str): The message for the commit.
    """
    if not os.path.isdir(repo_path) or not os.path.isdir(os.path.join(repo_path, '.git')):
        return f"Error: '{repo_path}' is not a valid Git repository."
    
    try:
        repo = git.Repo(repo_path)
        repo.git.add(A=True) # Stage all changes
        commit = repo.index.commit(commit_message)
        return f"Successfully created commit {commit.hexsha} with message: '{commit_message}'"
    except Exception as e:
        return f"An error occurred during git commit: {e}"