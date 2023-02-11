#!/usr/bin/env python3
"""
# Perform the necessary series of git operations to retrieve a set of subdirectories
# from a specific commit in a repository.
"""
import sys
import os
from contextlib import ExitStack
from subprocess import run as System
from pathlib import Path

default_commit = 'master'
sparse_clone_options = [
	'--sparse',
	'--filter=blob:none',
	'--no-checkout',
	'--depth=1',
	'--branch', # Optiona Argument supplied by usage context.
]

def identify_selections(rpaths):
	"""
	# Identify how the repository path is to be mapped locally.
	# Use '/./' as the means to identify re-mapped paths.
	"""
	for x in rpaths:
		try:
			repo_path, map_path = x.split('/./', 1)
		except ValueError:
			repo_path = x
			map_path = x

		yield (repo_path, map_path)

def git(tree, subcmd, *, command='git'):
	return [
		command,
		'--work-tree=' + str(tree),
		'--git-dir=' + str(tree/'.git'),
		subcmd,
	]

def environ_cache_path():
	env = os.environ['GITSELECTCACHE']
	if env.strip():
		# Non-empty string.
		return Path(env)
	else:
		# Empty setting defaults to home.
		return Path.home() / '.git-select-cache'

def pcache(ctx, repo, commit) -> Path:
	from hashlib import sha256 as Hash
	kh = Hash()
	kh.update((repo+commit).encode('utf-8'))
	return environ_cache_path()/kh.hexdigest()/commit

def tcache(ctx, repo, commit) -> Path:
	from tempfile import TemporaryDirectory as TD
	t = TD()
	path = ctx.enter_context(t)
	return Path(path) / commit

def main(argv):
	ctx = ExitStack()
	if 'GITSELECTCACHE' in os.environ:
		Cache = pcache
	else:
		Cache = tcache

	cmd, repo, commit, *paths = argv

	selections = list(identify_selections(paths))
	rpaths = [x[0] for x in selections]

	# Cache in home for now; temporary location is likely preferrable.
	with ctx:
		cache = Cache(ctx, repo, commit)

		if cache.exists():
			sys.stderr.write(f"git-select: Using cached clone {repr(str(cache))}.\n")
			System(git(cache, 'sparse-checkout') + ['set', '--no-cone'] + rpaths)
			System(git(cache, 'restore') + ['.'])
		else:
			System(['git', 'clone'] + sparse_clone_options + [commit, repo, str(cache)])
			System(git(cache, 'sparse-checkout') + ['set', '--no-cone'] + rpaths)
			System(git(cache, 'switch') + ['--detach', commit])

		targetroot = Path.cwd()
		for rpath, spath in selections:
			destination = targetroot.joinpath(spath)

			# Ignore if location is already in use.
			if destination.exists():
				sys.stderr.write(f"git-select: skipping {repr(str(destination))} as it already exists\n")
				continue

			# Only make the leading path of the destination.
			try:
				destination.parent.mkdir(parents=True)
			except FileExistsError:
				pass

			source = cache.joinpath(rpath)
			source.replace(destination)

if __name__ == '__main__':
	main(sys.argv)
