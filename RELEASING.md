# Creating a new release

This document is only relevant for maintainers of the openPMD validator repo.
It explains how to create a new release.

## Preparing your environment for a release

Make sure that your local environment is ready for a full release on
PyPI and conda. In particular:

- you should install the packages
[`pypandoc`](https://pypi.python.org/pypi/pypandoc/),
[`twine`](https://pypi.python.org/pypi/twine)
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

## Creating a release on Github

- The version number of the tool is `openPMDstandardVersion.patchLevel`, e.g.
  for the `1.1.0` release of the openPMD standard and the 5th release of the
  validator scripts: `1.1.0.5`

- Make sure that the version number in `setup.cfg`,
  `README.md`, `openpmd_validator/checkOpenPMD*.py` **and** in
  `openpmd_validator/createExamples*.py` correspond to
  the new release. Executing the script `newVersion.sh` will update all places
  for you.

- Document corresponding in `CHANGELOG.md`.

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

## Uploading the package to Conda

Once a new version is tagged and released on GitHub, an automatic bot will open a new pull request to [update the conda package on conda-forge](https://github.com/conda-forge/openpmd-validator-feedstock).
Review and merge that pull request to release an updated package.
