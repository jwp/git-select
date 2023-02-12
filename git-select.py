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
from collections.abc import Iterable

env_cache_id = 'GIT_SELECT_CACHE'
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
	"""
	# Necessary data for performing a copy of repository resources to the
	# local filesystem.
	"""
	rt_repository: str
	rt_snapshot: str
	rt_paths: list[str]
	rt_local_mappings: list[str]

	@property
	def rt_path_count(self) -> int:
		"""
		# Number of paths specified for copying.
		"""
		return len(self.rt_paths)

	@classmethod
	def from_selections(Class, repo, snapshot, selections):
		rp = []
		lm = []
		for p, m in selections:
			rp.append(p)
			lm.append(m)
		return Class(repo, snapshot, rp, lm)

	def translate(self, origin:Path, destination:Path) -> Iterable[tuple[Path, Path]]:
		"""
		# Convert the repository paths and local mappings held in the
		# structure to real Path instances.
		"""
		for rpath, spath in zip(self.rt_paths, self.rt_local_mappings):
			yield origin.joinpath(rpath), destination.joinpath(spath)

def git(tree, subcmd, *, command='git'):
	return [
		command,
		'--work-tree=' + str(tree),
		'--git-dir=' + str(tree/'.git'),
		subcmd,
	]

def environ_cache_path(env):
	setting = env[env_cache_id]

	if setting.strip():
		# Non-empty string.
		return Path(setting)
	else:
		# Empty setting defaults to home.
		return Path.home() / '.git-select-cache'

def pcache(env, rtx) -> Path:
	from hashlib import sha256 as Hash
	kh = Hash()
	kh.update((rtx.rt_repository).encode('utf-8'))
	return environ_cache_path(env)/kh.hexdigest()/rtx.rt_snapshot

def tcache(ctx, rtx) -> Path:
	from tempfile import TemporaryDirectory as TD
	t = TD()
	path = ctx.enter_context(t)
	return Path(path) / rtx.rt_snapshot

def scache(env, ctx, rtx) -> Path:
	if env_cache_id in env:
		return pcache(env, rtx)
	else:
		return tcache(ctx, rtx)

def execute_transfer(ctx, rtx:ResourceTransfer, clone:Path, fsroot:Path):
	"""
	# Perform the transfer by leveraging a sparse checkout against a shallow clone.

	# Files will be directly moved out of the work tree with pathlib.Path.replace,
	# and, in the case of a persistent cache, reinstated with git-restore.
	"""
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

	c = 0
	# Translate the relative repository paths and remappings into actual filesystem Paths.
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
		c += 1

	return c

def structure(argv):
	"""
	# Parse command argument vector.
	"""
	cmd, repo, commit, *paths = argv
	return repo, commit, identify_selections(paths)

def main(argv):
	"""
	# Interpret command arguments as a ResourceTransfer and execute it.
	"""

	rtx = ResourceTransfer.from_selections(*structure(argv))
	with ExitStack() as ctx:
		execute_transfer(ctx, rtx, scache(os.environ, ctx, rtx), Path.cwd())

if __name__ == '__main__':
	main(sys.argv)
