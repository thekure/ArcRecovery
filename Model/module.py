class Module:
    def __init__(self, name: str, parent_module: str, file_path: str):
        self.name = name
        self.parent_module = parent_module
        self.file_path = file_path
        self.dependencies = set()
        self.is_package = False
        self.depth = 0

    def get_dependencies(self):
        return self.dependencies

    def get_number_of_dependencies(self):
        return len(self.dependencies)
