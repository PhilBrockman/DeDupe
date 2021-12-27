import glob, os, pprint

def collect_files_from_directory(dir):
  hashmap = {}
  for f in glob.glob("./**", recursive=True):
    if os.path.isdir(f):
      name = os.path.basename(f)
      if name not in hashmap:
        hashmap[name] = []
      hashmap[name].append({
        "path": f,
        "file count": sum(len(files) for _, _, files in os.walk(f)),
      })

  return hashmap

foo = collect_files_from_directory(".")
pprint.pprint(foo)