#!/usr/bin/env python3
"""
# Perform the necessary series of git operations to retrieve a set of subdirectories
# from a specific commit in a repository.
"""
import sys
import os
from dataclasses import dataclass
from contextlib import ExitStack
from subprocess import run as System
from pathlib import Path

env_cache_id = 'GIT_SELECT_CACHE'
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

@dataclass
class ResourceTransfer(object):
	rt_repository: str
	rt_snapshot: str
	rt_paths: list[str]
	rt_local_mappings: list[str]

	@classmethod
	def from_selections(Class, repo, snapshot, selections):
		rp = []
		lm = []
		for p, m in selections:
			rp.append(p)
			lm.append(m)
		return Class(repo, snapshot, rp, lm)

	def translate(self, origin:Path, destination:Path):
		for rpath, spath in zip(self.rt_paths, self.rt_local_mappings):
			yield origin.joinpath(rpath), destination.joinpath(spath)

def git(tree, subcmd, *, command='git'):
	return [
		command,
		'--work-tree=' + str(tree),
		'--git-dir=' + str(tree/'.git'),
		subcmd,
	]

def environ_cache_path():
	env = os.environ[env_cache_id]
	if env.strip():
		# Non-empty string.
		return Path(env)
	else:
		# Empty setting defaults to home.
		return Path.home() / '.git-select-cache'

def pcache(ctx, rtx) -> Path:
	from hashlib import sha256 as Hash
	kh = Hash()
	kh.update((rtx.rt_repository).encode('utf-8'))
	return environ_cache_path()/kh.hexdigest()/rtx.rt_snapshot

def tcache(ctx, rtx) -> Path:
	from tempfile import TemporaryDirectory as TD
	t = TD()
	path = ctx.enter_context(t)
	return Path(path) / rtx.rt_snapshot

def execute_transfer(ctx, rtx:ResourceTransfer, clone:Path, fsroot:Path):
	# Cache in home for now; temporary location is likely preferrable.
	if clone.exists():
		sys.stderr.write(f"git-select: Using cached clone {repr(str(clone))}.\n")
		System(git(clone, 'sparse-checkout') + ['set', '--no-cone'] + rtx.rt_paths)
		System(git(clone, 'restore') + ['.'])
	else:
		System(['git', 'clone'] + sparse_clone_options + [
			rtx.rt_snapshot, rtx.rt_repository, str(clone)
		])
		System(git(clone, 'sparse-checkout') + ['set', '--no-cone'] + rtx.rt_paths)
		System(git(clone, 'switch') + ['--detach', rtx.rt_snapshot])

	for rpath, spath in rtx.translate(clone, fsroot):
		# Ignore if location is already in use.
		if spath.exists():
			sys.stderr.write(f"git-select: skipping {repr(str(spath))} as it already exists\n")
			continue

		# Only make the leading path.
		try:
			spath.parent.mkdir(parents=True)
		except FileExistsError:
			pass

		# Move if possible, if clone is reused, git-restore will be ran.
		rpath.replace(spath)

def main(argv):
	cmd, repo, commit, *paths = argv
	rtx = ResourceTransfer.from_selections(repo, commit, identify_selections(paths))
	with ExitStack() as ctx:
		if env_cache_id in os.environ:
			cache = pcache(ctx, rtx)
		else:
			cache = tcache(ctx, rtx)

		execute_transfer(ctx, rtx, cache, Path.cwd())

if __name__ == '__main__':
	main(sys.argv)
