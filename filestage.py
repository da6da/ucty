from __future__ import print_function

"""

"""

import os


class FileDir:
    def __init__(self, root, subdir):
        self.path = os.path.join(root, subdir)
        self.files = list(enumerate(self.list_files(self.path)))

    def create_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            return True
        else:
            return False

    @classmethod
    def list_files(cls, path):
        for root, dirs, files in os.walk(path):
            return files


class FileStageDB:
    def __init__(self, root, stages=None):
        self.root = root
        if stages is None:
            self.stages = {}
        else:
            self.stages = stages

    def add_stage(self, id, subdir):
        self.stages[id] = FileDir(self.root, subdir)

    def create_db_dirs(self, verbose=False):
        for sid, fd in self.stages.iteritems():
            if fd.create_path() and verbose:
                print("Creating stage {} directory {}".format(sid, self.stages[id].path))

    def dump(self):
        for sid, fs in self.stages.iteritems():
            print("Stage {} path {}".format(sid, fs.path))
            for x, n, fname, full_path in self.stage_files(sid):
                print("    file {} name {} ({})".format(n, fname, full_path))

    def stage_files(self, sid):
        fs = self.stages[sid]
        for n, fname in fs.files:
            yield sid, n, fname, os.path.join(fs.path, fname)

if __name__ == '__main__':
    fdb = FileStageDB(r"C:\tmp\fs")
    fdb.add_stage(1, "01")
    fdb.add_stage(2, "02")
    fdb.add_stage(3, "03")

    fdb.create_db_dirs(verbose=True)
    fdb.dump()
