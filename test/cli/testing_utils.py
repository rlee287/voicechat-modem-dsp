import os

class DirectoryChanger:
    def __init__(self, path):
        self.oldpath=os.getcwd()
        self.path=path
    
    def __enter__(self):
        os.chdir(self.path)
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.oldpath)

class FileCleanup:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        assert not os.path.exists(self.filename)
    def __exit__(self, exc_type, exc_val, exc_tb):
        assert os.path.isfile(self.filename)
        os.remove(self.filename)

class MockIO:
    def __init__(self, *, is_interactive, input_list):
        self.has_interactive=is_interactive
        self.input_list=input_list.copy()
    
    def is_interactive(self):
        return self.has_interactive
    
    def confirm(self, question, default, true_answer_regex):
        return self.input_list.pop(0)