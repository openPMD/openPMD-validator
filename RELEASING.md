# Creating a new release

This document is only relevant for maintainers of the openPMD validator repo.
It explains how to create a new release.

## Preparing your environment for a release

Make sure that your local environment is ready for a full release on
PyPI and conda. In particular:

- you should install the packages
[`pypandoc`](https://pypi.python.org/pypi/pypandoc/),
[`twine`](https://pypi.python.org/pypi/twine), [`pbr`](https://pypi.python.org/pypi/pbr)
- you should have a registered account on [PyPI](https://pypi.python.org/pypi) and [test PyPI](https://testpypi.python.org/pypi), and your `$HOME` should contain a file `.pypirc` which contains the following text:

```
[distutils]
index-servers=
    pypitest
    pypi

[pypitest]
repository = https://testpypi.python.org/pypi
username = <yourPypiUsername>

[pypi]
username = <yourPypiUsername>
```

- you should have a registered account on [Anaconda.org](https://anaconda.org/)

## Creating a release on Github

- The version number of the tool is `openPMDstandardVersion.patchLevel`, e.g.
  for the `1.1.0` release of the openPMD standard and the 5th release of the
  validator scripts: `1.1.0.5`

- Make sure that the version number in `setup.cfg`, `conda_recipe/meta.yaml`,
  `README.md`, `checkOpenPMD*.py` **and** in `createExamples*.py` correspond to
  the new release, and that the corresponding changes have been documented in
  `CHANGELOG.md`.

- Be aware that releases are maintained per branch.

- Create a GPG signed tag for a new version via `git tag -s` and push it to GitHub.

- Create a new release through the graphical interface on Github.
  Important: select the tag you uploaded for it!

## Uploading the package to PyPI

- Upload the package to [PyPI](https://pypi.python.org/pypi):
```bash
rm -rf dist
python2 setup.py sdist bdist_wheel
python3 setup.py sdist bdist_wheel
twine upload -s dist/* -r pypi
```
(NB: You can also first test this by uploading the package to
[test PyPI](https://testpypi.python.org/pypi) ; to do so, simply
replace `pypi` by `pypitest` in the above set of commands)

## Uploading the package to Anaconda.org

- `cd` into the folder `conda_recipe`.

- Still in the folder `conda_recipe`, run
```bash
docker build -t openpmd_validator_build .

# remove old files if present
rm -rf linux-64 linux-ppc64le osx-64 win-64

pfs="linux-64 osx-64 linux-ppc64le win-64"
for p in $pfs; do \
  docker run --rm -it -v $PWD:/home/ -e platform=$p openpmd_validator_build; \
done
```
This builds the conda packages for Python 2.7, 3.4, 3.5 and 3.6, using a
reproduceable environment.

- After the build, start the container again and upload with the following commands:
```bash
docker run -it -v $PWD:/home/ openpmd_validator_build /bin/bash

anaconda login
anaconda upload /home/osx-64/*
anaconda upload /home/linux-64/*
anaconda upload /home/linux-ppc64le/*
anaconda upload /home/win-64/*
```
