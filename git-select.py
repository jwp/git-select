#!/usr/bin/env python3
"""
# Perform the necessary series of git operations to retrieve a set of subdirectories
# from a specific branch in a repository.
"""
import sys
from hashlib import sha256 as Hash
from subprocess import run as System
from pathlib import Path

default_branch = 'master'
sparse_clone_options = [
	'--sparse',
	'--filter=blob:none',
	'--no-checkout',
	'--depth=1',
	'--branch', # Optiona Argument supplied by usage context.
]

def git(tree, subcmd, *, command='git'):
	return [
		command,
		'--work-tree=' + str(tree),
		'--git-dir=' + str(tree/'.git'),
		subcmd,
	]

def main(argv):
	branch = default_branch
	i = 1

	if argv[1] == '--branch':
		branch = argv[2]
		i = 3
	elif argv[1].startswith('--branch='):
		branch = argv[1].split('=', 1)[1]
		i = 2

	repo, *rpaths = argv[i:]

	# Identify how the repository path is to be mapped locally.
	# Use '/./' as the means to identify re-mapped paths.
	selections = []
	for x in rpaths:
		try:
			repo_path, map_path = x.split('/./', 1)
		except ValueError:
			repo_path = x
			map_path = x

		selections.append((repo_path, map_path))

	# Cache in home for now; temporary location is likely preferrable.
	cache_root = Path.home() / '.git-select-cache'
	kh = Hash()
	kh.update(repo.encode('utf-8'))
	key = kh.hexdigest()
	cache = cache_root/key/branch

	if cache.exists():
		sys.stderr.write('git-select: \n')
		System(git(cache, 'checkout') + ['.'])
	else:
		System(['git', 'clone'] + sparse_clone_options + [branch, repo, str(cache)])
		System(git(cache, 'sparse-checkout') + ['set', '--no-cone'] + [x[0] for x in selections])
		System(git(cache, 'switch') + [branch])

	targetroot = Path.cwd()
	for rpath, spath in selections:
		destination = targetroot.joinpath(spath)
		if destination.exists():
			sys.stderr.write('git-select: skipping {repr(destination)} as it already exists\n')
			continue
		source = cache.joinpath(rpath)
		source.replace(destination)

if __name__ == '__main__':
	main(sys.argv)
