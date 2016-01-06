openPMD Validator Scripts
=========================

This repository contains scripts to validate existing files that (claim to)
implement the [openPMD Standard](https://github.com/openPMD/openPMD-standard).

Additional scripts to create random/empty files with the valid markup of the
standard are also provided.


Rationale
---------

These tools are intended for developers that want to implementent the standard.
They were written to allow an easy *implement-test-correct* workflow without
the hazzle to check every word of the written standard twice.

Nevertheless, these scripts can not validate 100% of the standard and uncovered
sections shall be cross-checked manually with the words of the written
standard.

For more information on requirements for implementations, please refer to the
section
[*Implementations*](https://github.com/openPMD/openPMD/blob/1.0.0/STANDARD.md#implementations)
of the openPMD standard.


Development
-----------

The development of these scripts is carried out *per-branch*.
Each branch corresponds to a certain version of the standard and might
be updated in case tests did contain bugs or we found a way to cover more
sections of the standard.

[![Build Status](https://travis-ci.org/openPMD/openPMD-validator.svg?branch=1.0.0)](https://travis-ci.org/openPMD/openPMD-validator)
