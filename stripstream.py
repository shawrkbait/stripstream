#!/usr/libexec/platform-python

import dnf
import os
import sys

base = dnf.Base()
base.conf.read(filename="myrepo")
base.read_all_repos()
base.fill_sack()

modulename = sys.argv[1]
rmstream = sys.argv[2]

module_base = dnf.module.module_base.ModuleBase(base)
modulePackages, nsvcap = module_base.get_modules(modulename)

nonremovable = set()
removable = set()
artifact_names = set()
req_set = set()

for mp in modulePackages:
  if mp.getName() == modulename and mp.getStream() == rmstream:
    removable.update(mp.getArtifacts())
    for art in mp.getArtifacts():
      pkg_name = art.rsplit("-", 2)[0]
      artifact_names.add(pkg_name)
  else:
    nonremovable.update(mp.getArtifacts())

# Keep package if package is in other streams
removable = [ x for x in removable if x not in nonremovable ]

module_base.enable([modulename+':'+rmstream])

base_no_source_query = base.sack.query().filterm(arch__neq=['src','nosrc']).apply()
install_base_query = base_no_source_query.filter(nevra_strict=removable)

for n in artifact_names:
  query = install_base_query.filter(name=n)

  for p in query:
    loc = p.location
    if loc is None:
      continue
    repoloc = os.path.join(p.pkgdir, loc.lstrip("/"))
    if os.path.exists(repoloc):
      print(repoloc)

# TODO: If something depends on the module we want to remove, we must also remove that
# TODO: Remove metadata               
