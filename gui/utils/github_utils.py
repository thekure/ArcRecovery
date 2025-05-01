import re
import git
import os
import shutil
from constants import CODE_ROOT_FOLDER

def is_valid_github_url(url):
    github_pattern = r'^https?://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+/?$'
    return bool(re.match(github_pattern, url))

def clone_repository(url, path):
    """Clone a repository from URL to path."""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    git.Repo.clone_from(url, path)

def clear_repository(path):
    """Clear the contents of a directory."""
    if os.path.exists(path):
        shutil.rmtree(path)
        os.makedirs(path) 