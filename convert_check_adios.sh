# Copyright (c) 2015-2016 Axel Huebl, Michael Sippel
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
sed -e 's/h5py/adios/g' \
    -e 's/\.h5/\.bp/g' \
    -e 's/h5/ad/g' \
    -e "s/ad.is_hdf5.*(\(.*\))/\1.endswith('.bp')/g" \
    -e 's/, "w"//g' \
    -e 's/create_group/declare_group/g' \
    -e 's/create_dataset/define_var/g' \
    checkOpenPMD_h5.py > checkOpenPMD_adios.py

chmod u+x checkOpenPMD_adios.py

