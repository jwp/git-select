## Extract Resources from Specific Branches in git Repositories

A Python script implementing a prototype shorthand for sparse checkouts.
This has only been subject to brief manual testing with Python 3.11.

While adding a description of a sparse-checkout based installation method to
[py-postgreql](https://github.com/python-postgres/fe), it became obvious that
concision was necessary.

`git-select` performs a sparse checkout on a target repository selecting the cited repository
paths into the filesystem, relative to the current working directory.
The local clone of the repository is cached relative to the user's home directory for future use.

Optionally, the set of directories can be locally re-mapped in order avoid integration conflicts.

## Installation

This will not be published to PyPI.

```bash
git clone https://github.com/jwp/git-select jwp-git-select
```

## Usage

Select `postgresql` from py-postgresql:

```bash
python3 ./git-select.py --branch=v1.3 https://github.com/python-postgres/fe postgresql
```

Re-mapped to a different directory:

```bash
python3 ./git-select.py --branch=v1.3 https://github.com/python-postgres/fe postgresql/./pg
```
