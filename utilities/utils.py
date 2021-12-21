import glob, pprint

def collect_files_from_directory(dir, accepts=[".jpg", ".png", ".jpeg"]):
  hashmap = {}
  for f in glob.glob(f'{dir}/**/*', recursive=True):
    for ending in accepts:
      if(f.lower().endswith(ending)):
        print("image found")
        basename = f.split("/")[-1].lower()
        if basename not in hashmap:
          hashmap[basename] = []
        hashmap[basename].append(f)

  pprint.pprint(hashmap)
  return hashmap

