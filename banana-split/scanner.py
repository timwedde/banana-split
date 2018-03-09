from glob import glob
from os.path import join
from patterns import name_pattern

def scan(dir, pattern, recursive=False):
    return [{"name": name_pattern.match(file).group(2), "path": file} for file in glob(join(dir, pattern), recursive=recursive)]
