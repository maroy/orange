#! /usr/bin/env python

import os, re

#filenamedef=re.compile(r".*\.(.pp|px)$")
filenamedef=re.compile(r".*\..pp$")
includedef=re.compile(r'\s*#include\s*"(?P<filename>[^"]*)"')
filestemdef=re.compile(r'(?P<filestem>.*)\.(?P<fileextension>[^.]*)$')

dirs = ["orange", "statc", "corn", "include"]

def findfiles():
  files = {}
  for dir in dirs:
    for filename in os.listdir(dir):
      if filenamedef.match(filename):
        files[filename] = (dir, [])
  return files

ppp_timestamp_dep = []
px_timestamp_dep = []
px_files = []

def finddeps(filename):
  file=open(files[filename][0]+"/"+filename)
  lineno=0
  mydeps = files[filename][1]
  for line in file:
    lineno=lineno+1
    found=includedef.match(line)
    if not found:
      continue
      
    depname=os.path.split(found.group("filename"))[1]
    if (depname[-4:]==".ppp"):
      ppp_timestamp_dep.append(depname[:-4]+".hpp")
      mydeps.append(depname[:-4]+".hpp")
#      if not "$(PPPDIR)/timestamp.h" in mydeps:
#        mydeps.append("$(PPPDIR)/timestamp.h")
    else:
      if (depname[-3:]==".px"):
        if depname not in px_files: px_files.append( depname)
        if not filename in px_timestamp_dep:
          px_timestamp_dep.append(filename)
  #      if not "$(PXDIR)/timestamp.h" in mydeps:
  #        mydeps.append("$(PXDIR)/timestamp.h")

      if not depname in files and depname!="Python.h" and depname[-3:]!=".px" and depname[-2:]!=".i" and depname[-2:]!=".h":
        print "%s:%i: Warning: included file %s not found" % (filename, lineno, depname)
        continue
      else:
        mydeps.append(depname)    
    

def recdeps(rootname, filename):
  if not filename in deps[rootname]:
    if deps.has_key(filename) and (rootname!=filename):
      deps[rootname].update(deps[filename])
    else:
      deps[rootname][filename]=None
      for dep in files.get(filename, ("", []))[1]:
        recdeps(rootname, dep)


# The script is supposed to be run from directory
# 'source', so the below has been removed
# os.chdir(os.getenv("ORANGEHOME")+"/source")

files = findfiles()
for file in files:
  finddeps(file)

deps = {}  
for file in files:
  deps[file]={}
  recdeps(file, file)

deplist = deps.items()
deplist.sort(lambda x, y: cmp(x[0], y[0]))

dont_compile = ["im_col_assess.cpp"]
notorange = dont_compile+["corn.cpp", "statc.cpp"]

makedepsfile=open("makefile.deps", "wt")

makedepsfile.write("ORANGE_OBJECTS =")
cnt = 0

for file in deplist:
    if file[0][-4:]==".cpp" and not file[0] in notorange:
        if not cnt:
            makedepsfile.write("\\\n\t")
        cnt = (cnt+1) % 6
        makedepsfile.write(" obj/%s.o" % file[0][:-4])
            
makedepsfile.write("\n\n")

makedepsfile.write("CORN_OBJECTS = obj/corn.o obj/c2py.o\n\n")
makedepsfile.write("STATC_OBJECTS = obj/stat.o obj/statc.o  obj/c2py.o obj/statexceptions.o obj/lcomb.o\n\n")
 

for (file, filedeps) in deplist:
  if (file[-4:]==".cpp") and (not file in dont_compile):
    dl = filedeps.keys()
    dl.sort()
    makedepsfile.write("obj/%s.o : %s/%s.cpp %s\n" % (file[:-4], files[file][0], file[:-4], reduce(lambda a, b: a+" "+b, dl)))
makedepsfile.write("\n\n")

makedepsfile.write("orange/ppp/stamp: %s\n" % reduce(lambda a, b: a+" "+b, ppp_timestamp_dep))
makedepsfile.write("\tpython orange/devscripts/pyprops.py orange\n\n")

makedepsfile.write("orange/px/stamp: %s\n" % reduce(lambda a, b: a+" "+b, px_timestamp_dep))
makedepsfile.write("\tpython orange/devscripts/pyxtract.py orange\n\n")

for filename in px_files:
  makedepsfile.write("%s: \n\n" % filename)

makedepsfile.close()
