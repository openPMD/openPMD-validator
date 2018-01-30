#!/usr/bin/env bash
#
# Copyright 2017-2018 Axel Huebl
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

# This file is a maintainer tool to bump the versions inside the
# openPMD-validator repository at all places where necessary.

# Maintainer Inputs ###########################################################

echo "Hi there, this is a openPMD-validator maintainer tool to update the"
echo "source code of openPMD-validator to a new version number on all places"
echo "where necessary."
echo "For it to work, you need write access on the source directory and"
echo "you should be working in a clean git branch without ongoing"
echo "rebase/merge/conflict resolves and without unstaged changes."

# check source dir
REPO_DIR=$(cd $(dirname $BASH_SOURCE) && pwd)
echo
echo "Your current source directory is: $REPO_DIR"
echo

read -p "Are you sure you want to continue? [y/N] " -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "You did not confirm with 'y', aborting."
    exit 1
fi

echo "We will now run a few sed commands on your source directory."
echo "Please answer the following questions about the version number"
echo "you want to set first:"
echo

read -p "openPMD STANDARD MAJOR version? (e.g. 1) " -r
MAJOR=$REPLY
echo
read -p "openPMD STANDARD MINOR version? (e.g. 0) " -r
MINOR=$REPLY
echo
read -p "openPMD STANDARD PATCH version? (e.g. 0) " -r
PATCH=$REPLY
echo
read -p "openPMD VALIDATOR running version? (e.g. 5) " -r
VALIV=$REPLY
echo

if [[ -n "$SUFFIX" ]]
then
    SUFFIX_STR="-$SUFFIX"
fi

VERSION_STR="$MAJOR.$MINOR.$PATCH.$VALIV"

echo
echo "Your new version is: $VERSION_STR"
echo

read -p "Is this information correct? Will now start updating! [y/N] " -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "You did not confirm with 'y', aborting."
    exit 1
fi


# Updates #####################################################################

# regex for a 4 digit version number
regv="\([0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+\)"

# setup files
#   setuptools
sed -i "s/"\
"\(.*version='\)"$regv"\('.*\)/"\
"\1"$VERSION_STR"\3/" \
    $REPO_DIR/setup.py
#   conda
sed -i 's/'\
'\({% set version = "\)'$regv'\(".*\)/'\
'\1'$VERSION_STR'\3/' \
    $REPO_DIR/conda_recipe/meta.yaml

# example creator scripts
#   hdf5
sed -i 's/'\
'\("softwareVersion".*\)'$regv'\(")\)/'\
'\1'$VERSION_STR'\3/' \
    $REPO_DIR/openpmd_validator/createExamples_h5.py

# documentation
sed -i 's/'\
'\(.*validator==\)'$regv'\(.*\)/'\
'\1'$VERSION_STR'\3/' \
    $REPO_DIR/README.md
sed -i 's/'\
'\(.*validator[@-]\)'$regv'\(.*\)/'\
'\1'$VERSION_STR'\3/' \
    $REPO_DIR/README.md
sed -i 's/'\
'\(.*\)'$regv'\(\.tar\.gz\)/'\
'\1'$VERSION_STR'\3/' \
    $REPO_DIR/README.md

# Epilog ######################################################################

echo
echo "Done. Please check your source, e.g. via"
echo "  git diff"
echo "now and commit the changes if no errors occured."
