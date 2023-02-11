## Extract Resources from Specific Branches in git Repositories

A Python script implementing a prototype shorthand for sparse checkouts.
This has only been subject to brief manual testing with Python 3.11.

While adding a description of a sparse-checkout based installation method to
[py-postgreql](https://github.com/python-postgres/fe), it became obvious that
concision was necessary.

`git-select` performs a sparse checkout on a target repository selecting the cited repository
paths into the filesystem, relative to the current working directory.
The local clone of the repository is cached relative to the user's home directory temporarily
or permentantly for future use.

Directory structure is maintained by default; any leading paths to a particular repository
sub-directory will be maintained. Optionally, the selected resource may be remapped by
extending the path with `/./local-path`. Where `local-path` is the desired local destination.

## Installation

This will not be published to PyPI.

```bash
git clone https://github.com/jwp/git-select jwp-git-select
# Or any directory in PATH. '~/.gitbin' has no special semantics.
mkdir ~/.gitbin
cp jwp-git-select/git-select.py ~/.gitbin/git-select
chmod a+x ~/.gitbin/git-select
# If necessary.
PATH="$PATH:$HOME/.gitbin"
```

The script will be executed using `/usr/bin/env python3` by default.

## Usage

Presumes that installation was performed; alternatively, execute using Python
directly by replacing `git select` with `python3 jwp-git-select/git-select.py`.

Select `postgresql` from py-postgresql:

```bash
git select --branch=v1.3 https://github.com/python-postgres/fe postgresql
```

Re-mapped to a different directory:

```bash
git select --branch=v1.3 https://github.com/python-postgres/fe postgresql/./pg
```

## Repository Slice References

Idea mode. Consolidated IRI syntax may be useful as well:

```bash
git cp https://github.com/python-postgres/fe#v1.3/postgresql ./pg
```

Where the trailing slash indicates that no remapping should be performed.

## Rationale

Ultimately, this is to ease the deployment of software that can be integrated with `cp -r` given
that resources were already available on the filesystem. For many pure-Python projects, no
processing of the source is required for usage. When that is the case, deploying to a temporary
package directory can be the preferred means of installation for informal environments.
