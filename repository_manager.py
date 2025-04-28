import os
import shutil
import git

class RepositoryManager:
    def __init__(self, repo_url, dest_dir="cur_repo"):
        self.repo_url = repo_url
        self.dest_dir = dest_dir

    def clone_repo(self):
        if os.path.exists(self.dest_dir):
            print(f"Removing existing {self.dest_dir} folder...")
            shutil.rmtree(self.dest_dir)
        print(f"Cloning {self.repo_url} into {self.dest_dir}")
        git.Repo.clone_from(self.repo_url, self.dest_dir)

    def find_python_files(self):
        python_files = []
        for root, _, files in os.walk(self.dest_dir):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    python_files.append(full_path)
        return python_files

    def get_repo_path(self):
        return self.dest_dir 