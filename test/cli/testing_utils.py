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
    def __exit__(self):
        assert os.path.isfile(self.filename)
        os.remove(self.filename)