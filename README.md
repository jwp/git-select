## Extract Specific Resources from git Repositories

A Python script implementing a prototype shorthand for extracting repository resources.
Think `cp -r`, but with shallow clones and sparse checkouts providing the source.

`git-select` performs a sparse checkout on a target repository and recursively copies the
cited repository paths into the filesystem, relative to the working directory.
The local clone of the repository is kept temporarily for the duration of the process
or permanently when `GIT_SELECT_CACHE` environment variable is set to an empty string or a directory
path. When set to an empty string, the `~/.git-select-cache` path is used.

Directory structure is maintained by default; any leading directories to a particular repository
path will be maintained. Optionally, the selected resource may be remapped by
extending the path with `/./local-path`. Where `local-path` is the desired filesystem destination.
`/./` being the signal used to identify that the path should be remapped.

### Defects

- Limited argument parsing; no --help.
- Cache should be controllable with arguments.
- Per-commit shallow clones; no sharing with persistent cache.
- No tests.
- Shell was probably sufficient.

### Installation

This will not be published to PyPI.

From a raw github resource:

```bash
# Or any directory in PATH. '~/.gitbin' has no special semantics.
(pathdir="$HOME/.gitbin"
test -e "$pathdir" || mkdir "$pathdir"
curl https://raw.githubusercontent.com/jwp/git-select/main/git-select.py >"$pathdir/git-select"
chmod a+x "$pathdir/git-select")
```

From a usual clone:

```bash
git clone https://github.com/jwp/git-select jwp-git-select
# Or any directory in PATH. '~/.gitbin' has no special semantics.
test -e ~/.gitbin || mkdir ~/.gitbin
cp jwp-git-select/git-select.py ~/.gitbin/git-select
chmod a+x ~/.gitbin/git-select
# If necessary.
PATH="$PATH:$HOME/.gitbin"
```

The script will be executed using `/usr/bin/env python3` by default.

### Usage

Presumes that installation was performed; alternatively, execute using Python
directly by replacing `git select` with `python3 jwp-git-select/git-select.py`.
Tags should work. Whatever `--branch` accepts.

Select `git-select.py` from jwp/git-select repository:

```bash
git select https://github.com/jwp/git-select main git-select.py
test -e git-select.py
```

Remapped to a different local path:

```bash
git select https://github.com/jwp/git-select main git-select.py/./gs.py
test -e gs.py
```

Copying multiple paths:

```bash
git select https://github.com/jwp/git-select main git-select.py README.md
test -e git-select.py && test -e README.md
```

Remapped leading path using trailing `/`:

```bash
git select https://github.com/jwp/git-select main git-select.py/./new/path/
test -e new/path/git-select.py
```

### Rationale

Likely implemented dozens of times with plain clones,
this implementation leverages shallow clones and sparse checkouts.

Primarily, this is to ease the deployment of software that can be integrated with `cp -r` given
that resources were already available on the filesystem. For many pure-Python projects, no
processing of the source is required for usage. When that is the case, deploying to a temporary
package directory can be the preferred means of installation for informal environments.

`/./` is the chosen remapping signal as `/./` is *usually* a no-op when present in filesystem
paths; worst case with most environments is that a user has to resolve any `.` in a composed
path to avoid triggering remapped pathing.

### Alternatives and Discussion

If only temporary clones were used,
services like `https://raw.githubusercontent.com` *could* provide a superior solution by providing
access to archives of repository "slices". However, without some attempt to standardize the means to
resolve the access point, we would be subjected to duplicate repository identities for each
host provider. Using a single canonical IRI (SCM Repository) has the advantage of reducing the
required knowledge. It is possible to achieve this with HTTP without a parallel service, but
no providers appear to offer the feature.

`git cp` may be a better name. Consolidated IRI syntax may be useful as well:

```bash
git cp https://github.com/jwp/git-select#main/git-select.py ./gs
# Or where the commit (branch/tag) is expected to be provided the context.
git cp -@main https://github.com/jwp/git-select#/git-select.py ./gs
```

Remapping paths could be supported using `./` and `/` as signals. Where a path argument starting
with either `./` or `/` indicates that the previous repository path should be renamed when
the copy is performed.
