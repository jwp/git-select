## Extract Specific Resources from git Repositories

A Python script implementing a prototype shorthand for extracting repository resources.
Think `cp -r`, but with shallow git repositories and sparse checkouts as a source.

While adding a description of a sparse-checkout based installation method to
[py-postgreql](https://github.com/python-postgres/fe), it became evident that
concision would be helpful.

`git-select` performs a sparse checkout on a target repository and recursively copies the
cited repository paths into the filesystem, relative to the working directory.
The local clone of the repository is cached relative to the user's home directory temporarily
or permentantly for future use.

Directory structure is maintained by default; any leading paths to a particular repository
sub-directory will be maintained. Optionally, the selected resource may be remapped by
extending the path with `/./local-path`. Where `local-path` is the desired filesystem destination.

### Defects

- Limited argument parsing; no --help.
- Cache is currently permanent. (rm -rf ~/.git-select-cache)
- No tag support. (yet)
- No tests.
- Shell was probably sufficient.

### Installation

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

### Usage

Presumes that installation was performed; alternatively, execute using Python
directly by replacing `git select` with `python3 jwp-git-select/git-select.py`.

Select `postgresql` from py-postgresql:

```bash
git select --branch=v1.3 https://github.com/python-postgres/fe postgresql
```

Remapped to a different directory:

```bash
git select --branch=v1.3 https://github.com/python-postgres/fe postgresql/./pg
```

Multiple paths:

```bash
git select --branch=v1.3 https://github.com/python-postgres/fe postgresql/types postgresql/protocol
```

### Repository Slice References

Idea mode. Consolidated IRI syntax may be useful as well:

```bash
git cp https://github.com/python-postgres/fe#v1.3/postgresql ./pg
```

Where the trailing slash indicates that no remapping should be performed.

### Rationale

Likely implemented dozens of times with plain clones,
this implementation leverages shallow clones and sparse checkouts.

Ultimately, this is to ease the deployment of software that can be integrated with `cp -r` given
that resources were already available on the filesystem. For many pure-Python projects, no
processing of the source is required for usage. When that is the case, deploying to a temporary
package directory can be the preferred means of installation for informal environments.
