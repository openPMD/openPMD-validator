#!/usr/bin/env python
#
# Copyright (c) 2015-2017 Axel Huebl, Remi Lehe
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

import h5py as h5
import numpy as np
import datetime
from dateutil.tz import tzlocal
import sys
import socket


def get_basePath(f, iteration):
    """
    Get the basePath for a certain iteration

    Parameter
    ---------
    f : an h5py.File object
        The file in which to write the data
    iteration : an iteration number

    Returns
    -------
    A string with a in-file path.
    """
    iteration_str = np.string_(str(iteration))
    return np.string_(f.attrs["basePath"]).replace(b"%T", iteration_str)

def setup_base_path(f, iteration):
    """
    Write the basePath group for `iteration`

    Parameters
    ----------
    f : an h5py.File object
        The file in which to write the data

    iteration : int
        The iteration number for this output
    """
    # Create the corresponding group
    base_path = get_basePath(f, iteration)
    f.create_group( base_path )
    bp = f[ base_path ]

    # Required attributes
    bp.attrs["time"] = 0.  # Value expressed in femtoseconds
    bp.attrs["dt"] = 0.5   # Value expressed in femtoseconds
    bp.attrs["timeUnitSI"] = np.float64(1.e-15) # Conversion factor

def get_software_dependencies():
    """
    Returns the software dependencies of this script as a semicolon
    separated string.
    """
    return np.string_(
        "python@{0}.{1}.{2};".format(
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro
        ) +
        "numpy@{0};".format( np.__version__ ) +
        "hdf5@{0};".format( h5.version.hdf5_version ) +
        "h5py@{0}".format( h5.__version__)
    )

def setup_root_attr(f):
    """
    Write the root metadata for this file

    Parameter
    ---------
    f : an h5py.File object
        The file in which to write the data
    """

    # extensions list
    ext_list = [["ED-PIC", np.uint32(1)]]

    # Required attributes
    f.attrs["openPMD"] = np.string_("1.1.0")
    f.attrs["openPMDextension"] = ext_list[0][1] # ED-PIC extension is used
    f.attrs["basePath"] = np.string_("/data/%T/")
    f.attrs["meshesPath"] = np.string_("meshes/")
    f.attrs["particlesPath"] = np.string_("particles/")
    f.attrs["iterationEncoding"] = np.string_("groupBased")
    f.attrs["iterationFormat"] = np.string_("/data/%T/")

    # Recommended attributes
    f.attrs["author"] = np.string_("Axel Huebl <a.huebl@hzdr.de>")
    f.attrs["software"] = np.string_("openPMD Example Script")
    f.attrs["softwareVersion"] = np.string_("1.1.0.3")
    f.attrs["softwareDependencies"] = get_software_dependencies()
    f.attrs["machine"] = np.string_(socket.gethostname())
    f.attrs["date"] = np.string_(
        datetime.datetime.now(tzlocal()).strftime('%Y-%m-%d %H:%M:%S %z'))

    # Optional
    f.attrs["comment"] = np.string_("This is a dummy file for test purposes.")


def write_rho_cylindrical(meshes, mode0, mode1):
    """
    Write the metadata and the data associated with the scalar field rho,
    using the cylindrical representation (with azimuthal decomposition
    going up to m=1)

    Parameters
    ----------
    meshes : an h5py.Group object
             Group of the meshes in basePath + meshesPath

    mode0 : a 2darray of reals
        The values of rho in the azimuthal mode 0, on the r-z grid
        (The first axis corresponds to r, and the second axis corresponds to z)

    mode1 : a 2darray of complexs
        The values of rho in the azimuthal mode 1, on the r-z grid
        (The first axis corresponds to r, and the second axis corresponds to z)
    """
    # Path to the rho meshes, within the h5py file
    full_rho_path = np.string_("rho")
    meshes.create_dataset( full_rho_path, (3, mode0.shape[0], mode0.shape[1]), \
                           dtype=np.float32)
    rho = meshes[full_rho_path]
    rho.attrs["comment"] = np.string_(
        "Density of electrons in azimuthal decomposition")

    # Create the dataset (cylindrical with azimuthal modes up to m=1)
    # The first axis has size 2m+1
    rho.attrs["geometry"] = np.string_("thetaMode")
    rho.attrs["geometryParameters"] = np.string_("m=1; imag=+")

    # Add information on the units of the data
    rho.attrs["unitSI"] = np.float64(1.0)
    rho.attrs["unitDimension"] = \
       np.array([-3.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #           L    M    T    I  theta  N    J
       # rho is in Coulomb per meter cube: C / m^3 = A * s / m^3 -> L^-3 * T * I

    # Add time information
    rho.attrs["timeOffset"] = 0. # Time offset with basePath's time

    # Add information on the r-z grid
    rho.attrs["gridSpacing"] = np.array([1.0, 1.0], dtype=np.float32)  # dr, dz
    rho.attrs["gridGlobalOffset"] = np.array([0.0, 0.0], dtype=np.float32) 
    rho.attrs["position"] = np.array([0.0, 0.0], dtype=np.float32)
    rho.attrs["gridUnitSI"] = np.float64(1.0)
    rho.attrs["dataOrder"] = np.string_("C")
    rho.attrs["axisLabels"] = np.array([b"r",b"z"])
    
    # Add specific information for PIC simulations
    add_EDPIC_attr_meshes(rho)

    # Fill the array with the field data
    if mode0.shape != mode1.shape :
        raise ValueError("`mode0` and `mode1` should have the same shape")
    rho[0,:,:] = mode0[:,:] # Store the mode 0 first
    rho[1,:,:] = mode1[:,:].real # Then store the real part of mode 1
    rho[2,:,:] = mode1[:,:].imag # Then store the imaginary part of mode 1

def write_b_2d_cartesian(meshes, data_ez):
    """
    Write the metadata and the data associated with the vector field B,
    using a 2d Cartesian representation.
    In this special case, the components of the vector field B.x and B.y
    shall be constant.

    Parameters
    ----------
    meshes : an h5py.Group object
             Group of the meshes in basePath + meshesPath
    data_ez : 2darray of reals
        The values of the component B.z on the 2d x-y grid
        (The first axis corresponds to x, and the second axis corresponds to y)
    """
    # Path to the E field, within the h5py file
    full_b_path_name = b"B"
    meshes.create_group(full_b_path_name)
    B = meshes[full_b_path_name]

    # Create the dataset (2d cartesian grid)
    B.create_group(b"x")
    B.create_group(b"y")
    B.create_dataset(b"z", data_ez.shape, dtype=np.float32)

    # Write the common metadata for the group
    B.attrs["geometry"] = np.string_("cartesian")
    B.attrs["gridSpacing"] = np.array([1.0, 1.0], dtype=np.float32)   # dx, dy
    B.attrs["gridGlobalOffset"] = np.array([0.0, 0.0], dtype=np.float32)  
    B.attrs["gridUnitSI"] = np.float64(1.0)
    B.attrs["dataOrder"] = np.string_("C")
    B.attrs["axisLabels"] = np.array([b"x",b"y"])
    B.attrs["unitDimension"] = \
       np.array([0.0, 1.0, -2.0, -1.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #          L    M     T     I  theta  N    J
       # B is in Tesla : kg / (A * s^2) -> M * T^-2 * I^-1

    # Add specific information for PIC simulations at the group level
    add_EDPIC_attr_meshes(B)

    # Add time information
    B.attrs["timeOffset"] = 0.25 # Time offset with basePath's time

    # Write attribute that is specific to each dataset:
    # - Staggered position within a cell
    B["x"].attrs["position"] = np.array([0.0, 0.0], dtype=np.float32)
    B["y"].attrs["position"] = np.array([0.0, 0.0], dtype=np.float32)
    B["z"].attrs["position"] = np.array([0.5, 0.5], dtype=np.float32)
    # - Conversion factor to SI units
    B["x"].attrs["unitSI"] = np.float64(3.3)
    B["y"].attrs["unitSI"] = np.float64(3.3)
    B["z"].attrs["unitSI"] = np.float64(3.3)

    # Fill the array with the field data
    #   the constant record components B.x and B.y have the same shape
    #   (== same mesh discretization) as the non-constant record
    #   component B.z
    B["x"].attrs["value"] = np.float(0.0)
    B["x"].attrs["shape"] = np.array(data_ez.shape, dtype=np.uint64)
    B["y"].attrs["value"] = np.float(0.0)
    B["y"].attrs["shape"] = np.array(data_ez.shape, dtype=np.uint64)
    B["z"][:,:] =  data_ez[:,:]

def write_e_2d_cartesian(meshes, data_ex, data_ey, data_ez ):
    """
    Write the metadata and the data associated with the vector field E,
    using a 2d Cartesian representation

    Parameters
    ----------
    meshes : an h5py.Group object
             Group of the meshes in basePath + meshesPath

    data_ex, data_ey, data_ez : 2darray of reals
        The values of the components E.x, E.y, E.z on the 2d x-y grid
        (The first axis corresponds to x, and the second axis corresponds to y)
    """
    # Path to the E field, within the h5py file
    full_e_path_name = b"E"
    meshes.create_group(full_e_path_name)
    E = meshes[full_e_path_name]

    # Create the dataset (2d cartesian grid)
    E.create_dataset(b"x", data_ex.shape, dtype=np.float32)
    E.create_dataset(b"y", data_ey.shape, dtype=np.float32)
    E.create_dataset(b"z", data_ez.shape, dtype=np.float32)

    # Write the common metadata for the group
    E.attrs["geometry"] = np.string_("cartesian")
    E.attrs["gridSpacing"] = np.array([1.0, 1.0], dtype=np.float32)  # dx, dy
    E.attrs["gridGlobalOffset"] = np.array([0.0, 0.0], dtype=np.float32)  
    E.attrs["gridUnitSI"] = np.float64(1.0)
    E.attrs["dataOrder"] = np.string_("C")
    E.attrs["axisLabels"] = np.array([b"x",b"y"])
    E.attrs["unitDimension"] = \
       np.array([1.0, 1.0, -3.0, -1.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #          L    M     T     I  theta  N    J
       # E is in volts per meters: V / m = kg * m / (A * s^3)
       # -> L * M * T^-3 * I^-1

    # Add specific information for PIC simulations at the group level
    add_EDPIC_attr_meshes(E)

    # Add time information
    E.attrs["timeOffset"] = 0.  # Time offset with respect to basePath's time

    # Write attribute that is specific to each dataset:
    # - Staggered position within a cell
    E["x"].attrs["position"] = np.array([0.0, 0.5], dtype=np.float32)
    E["y"].attrs["position"] = np.array([0.5, 0.0], dtype=np.float32)
    E["z"].attrs["position"] = np.array([0.0, 0.0], dtype=np.float32)
    # - Conversion factor to SI units
    E["x"].attrs["unitSI"] = np.float64(1.0e9)
    E["y"].attrs["unitSI"] = np.float64(1.0e9)
    E["z"].attrs["unitSI"] = np.float64(1.0e9)
    
    # Fill the array with the field data
    E["x"][:,:] =  data_ex[:,:]
    E["y"][:,:] =  data_ey[:,:]
    E["z"][:,:] =  data_ez[:,:]


def add_EDPIC_attr_meshes(field):
    """
    Write the metadata which is specific to PIC algorithm
    for a given field

    Parameters
    ----------
    field : an h5py.Group or h5py.Dataset object
            The record of the field (Group for vector mesh
            and Dataset for scalar meshes)

    """
    field.attrs["fieldSmoothing"] = np.string_("none")
    # field.attrs["fieldSmoothingParameters"] = \
    #     np.string_("period=10;numPasses=4;compensator=true")


def add_EDPIC_attr_particles(particle):
    """
    Write the metadata which is specific to the PIC algorithm
    for a given species.

    Parameters
    ----------
    particle : an h5py.Group object
               The group of the particle that gets additional attributes.

    """
    particle.attrs["particleShape"] = 3.0
    particle.attrs["currentDeposition"] = np.string_("Esirkepov")
    # particle.attrs["currentDepositionParameters"] = np.string_("")
    particle.attrs["particlePush"] = np.string_("Boris")
    particle.attrs["particleInterpolation"] = np.string_("uniform")
    particle.attrs["particleSmoothing"] = np.string_("none")
    # particle.attrs["particleSmoothingParameters"] = \
    #     np.string_("period=1;numPasses=2;compensator=false")


def write_meshes(f, iteration):
    full_meshes_path = get_basePath(f, iteration) + f.attrs["meshesPath"]
    f.create_group(full_meshes_path)
    meshes = f[full_meshes_path]

    # Extension: Additional attributes for ED-PIC
    meshes.attrs["fieldSolver"] = np.string_("Yee")
    meshes.attrs["fieldBoundary"] = np.array(
        [b"periodic", b"periodic", b"open", b"open"])
    meshes.attrs["particleBoundary"] = np.array(
        [b"periodic", b"periodic", b"absorbing", b"absorbing"])
    meshes.attrs["currentSmoothing"] = np.string_("Binomial")
    meshes.attrs["currentSmoothingParameters"] = \
         np.string_("period=1;numPasses=2;compensator=false")
    meshes.attrs["chargeCorrection"] = np.string_("none")

    # (Here the data is randomly generated, but in an actual simulation,
    # this would be replaced by the simulation data.)

    # - Write rho
    # Mode 0 : real values, mode 1 : complex values
    data_rho0 = np.random.rand(32,64)
    data_rho1 = np.random.rand(32,64) + 1.j*np.random.rand(32,64)
    write_rho_cylindrical(meshes, data_rho0, data_rho1)

    # - Write E
    data_ex = np.random.rand(32,64)
    data_ey = np.random.rand(32,64)
    data_ez = np.random.rand(32,64)
    write_e_2d_cartesian( meshes, data_ex, data_ey, data_ez )

    # - Write B
    data_bz = np.random.rand(32,64)
    write_b_2d_cartesian( meshes, data_bz )

def write_particles(f, iteration):
    fullParticlesPath = get_basePath(f, iteration) + f.attrs["particlesPath"]
    f.create_group(fullParticlesPath + b"electrons")
    electrons = f[fullParticlesPath + b"electrons"]

    globalNumParticles = 128 # example number of all particles

    electrons.attrs["comment"] = np.string_("My first electron species")

    # Extension: ED-PIC Attributes
    #   required
    add_EDPIC_attr_particles(electrons)
    #   recommended
    # currently none

    # constant scalar particle records (that could also be variable records)
    electrons.create_group(b"charge")
    charge = electrons["charge"]
    charge.attrs["value"] = -1.0
    charge.attrs["shape"] = np.array([globalNumParticles], dtype=np.uint64)
    # macroWeighted: False(0) the charge value is given for an underlying,
    #                real particle
    # weightingPower == 1: the charge of the macro particle scales linearly
    #                      with the number of underlying real particles
    #                      it represents
    charge.attrs["macroWeighted"] = np.uint32(0)
    charge.attrs["weightingPower"] = np.float64(1.0)
    # attributes from the base standard
    charge.attrs["timeOffset"] = 0.
    charge.attrs["unitSI"] = np.float64(1.60217657e-19)
    charge.attrs["unitDimension"] = \
       np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #          L    M    T    I  theta  N    J
       # C = A * s

    electrons.create_group(b"mass")
    mass = electrons["mass"]
    mass.attrs["value"] = 1.0
    mass.attrs["shape"] = np.array([globalNumParticles], dtype=np.uint64)
    # macroWeighted: False(0) the mass value is given for an underlying,
    #                real particle
    # weightingPower == 1: the mass of the macro particle scales linearly
    #                      with the number of underlying real particles
    #                      it represents
    mass.attrs["macroWeighted"] = np.uint32(0)
    mass.attrs["weightingPower"] = np.float64(1.0)
    # attributes from the base standard
    mass.attrs["timeOffset"] = 0.
    mass.attrs["unitSI"] = np.float64(9.10938291e-31)
    mass.attrs["unitDimension"] = \
       np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #          L    M    T    I  theta  N    J

    # scalar particle records (non-const/individual per particle)
    electrons.create_dataset(b"weighting", (globalNumParticles,),
                             dtype=np.float32)
    weighting = electrons["weighting"]
    # macroWeighted: True(1) by definition
    # weightingPower == 1: since this is the identity of weighting,
    #                      it scales linearly with itself
    weighting.attrs["macroWeighted"] = np.uint32(1)
    weighting.attrs["weightingPower"] = np.float64(1.0)
    # attributes from the base standard
    weighting.attrs["timeOffset"] = 0.
    weighting.attrs["unitSI"] = np.float64(1.0)
    weighting.attrs["unitDimension"] = \
       np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ], dtype=np.float64) 
    # plain floating point number
       
    # Position of each particle
    electrons.create_group(b"position")
    position = electrons["position"]
    position.create_dataset("x", (globalNumParticles,), dtype=np.float32)
    position.create_dataset("y", (globalNumParticles,), dtype=np.float32)
    position.create_dataset("z", (globalNumParticles,), dtype=np.float32)
    # Conversion factor to SI units
    position["x"].attrs["unitSI"] = np.float64(1.e-9)
    position["y"].attrs["unitSI"] = np.float64(1.e-9)
    position["z"].attrs["unitSI"] = np.float64(1.e-9)
    # macroWeighted: can be 1 or 0 in this case, since it's the same for macro
    #                particles and representing underlying particles
    # weightingPower == 0: the position does not scale with the weighting
    position.attrs["macroWeighted"] = np.uint32(1)
    position.attrs["weightingPower"] = np.float64(0.0)
    # attributes from the base standard
    position.attrs["timeOffset"] = 0.
    position.attrs["unitDimension"] = \
       np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #          L    M     T    I  theta  N    J
       # Dimension of Length per component

    # Position offset of each particle
    electrons.create_group(b"positionOffset")
    offset = electrons["positionOffset"]
    # Constant components here (typical of a moving window along z)
    offset.create_group(b"x")
    offset["x"].attrs["value"] = np.float32(0.)
    offset["x"].attrs["shape"] = np.array([globalNumParticles], dtype=np.uint64)
    offset.create_group(b"y")
    offset["y"].attrs["value"] = np.float32(0.)
    offset["y"].attrs["shape"] = np.array([globalNumParticles], dtype=np.uint64)
    offset.create_group(b"z")
    offset["z"].attrs["value"] = np.float32(100.)
    offset["z"].attrs["shape"] = np.array([globalNumParticles], dtype=np.uint64)
    # Conversion factor to SI units
    offset["x"].attrs["unitSI"] = np.float64(1.e-9)
    offset["y"].attrs["unitSI"] = np.float64(1.e-9)
    offset["z"].attrs["unitSI"] = np.float64(1.e-9)
    # macroWeighted: can be 1 or 0 in this case, since it's the same for macro
    #                particles and representing underlying particles
    # weightingPower == 0: the positionOffset does not scale with the weighting
    offset.attrs["macroWeighted"] = np.uint32(1)
    offset.attrs["weightingPower"] = np.float64(0.0)
    # attributes from the base standard
    offset.attrs["timeOffset"] = 0.
    offset.attrs["unitDimension"] = \
       np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #          L    M     T    I  theta  N    J
       # Dimension of Length per component
    
    # Momentum of each particle
    electrons.create_group(b"momentum")
    momentum = electrons["momentum"]
    momentum.create_dataset("x", (globalNumParticles,), dtype=np.float32)
    momentum.create_dataset("y", (globalNumParticles,), dtype=np.float32)
    momentum.create_dataset("z", (globalNumParticles,), dtype=np.float32)
    # Conversion factor to SI units
    momentum["x"].attrs["unitSI"] = np.float64(1.60217657e-19)
    momentum["y"].attrs["unitSI"] = np.float64(1.60217657e-19)
    momentum["z"].attrs["unitSI"] = np.float64(1.60217657e-19)
    
    # macroWeighted: True(1) in this example we store the momentum
    #                of the macro particle
    # weightingPower == 1: each underlying particle contributes linearly
    #                      to the total momentum
    momentum.attrs["macroWeighted"] = np.uint32(1)
    momentum.attrs["weightingPower"] = np.float64(1.0)
    # attributes from the base standard
    momentum.attrs["timeOffset"] = 0.25
    momentum.attrs["unitDimension"] = \
       np.array([1.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0 ], dtype=np.float64)
       #          L    M     T    I  theta  N    J
       # Dimension of Length * Mass / Time

    # Sub-Group `particlePatches`
    #   recommended
    mpi_size = 4  # "emulate" example MPI run with 4 ranks
    # 2 + 2 * Dimensionality of position record
    grid_layout = np.array( [512, 128, 1] ) # global grid in cells
    electrons.create_group(b"particlePatches")
    particlePatches = electrons["particlePatches"]

    particlePatches.create_dataset("numParticles", (mpi_size,), dtype=np.uint64)
    particlePatches.create_dataset("numParticlesOffset", (mpi_size,), dtype=np.uint64)
    particlePatches.create_dataset("offset/x", (mpi_size,), dtype=np.float32)
    particlePatches.create_group(b"offset/y")
    particlePatches.create_group(b"offset/z")
    particlePatches["offset/x"].attrs["unitSI"] = offset["x"].attrs["unitSI"]
    particlePatches["offset/y"].attrs["unitSI"] = offset["y"].attrs["unitSI"]
    particlePatches["offset/z"].attrs["unitSI"] = offset["z"].attrs["unitSI"]
    particlePatches.create_dataset("extent/x", (mpi_size,), dtype=np.float32)
    particlePatches.create_group(b"extent/y")
    particlePatches.create_group(b"extent/z")
    particlePatches["extent/x"].attrs["unitSI"] = offset["x"].attrs["unitSI"]
    particlePatches["extent/y"].attrs["unitSI"] = offset["y"].attrs["unitSI"]
    particlePatches["extent/z"].attrs["unitSI"] = offset["z"].attrs["unitSI"]

    # domain decomposition shall be 1D along x (but positions are still 3D)
    # we can therefor make the other components constant
    particlePatches["offset/y"].attrs["value"] = np.float32(0.0)   # full size
    particlePatches["offset/z"].attrs["value"] = np.float32(0.0)   # full size
    particlePatches["offset/y"].attrs["shape"] = np.array([mpi_size], dtype=np.uint64)
    particlePatches["offset/z"].attrs["shape"] = np.array([mpi_size], dtype=np.uint64)

    particlePatches["extent/y"].attrs["value"] = np.float32(128.0) # full size
    particlePatches["extent/z"].attrs["value"] = np.float32(1.0)   # full size
    particlePatches["extent/y"].attrs["shape"] = np.array([mpi_size], dtype=np.uint64)
    particlePatches["extent/z"].attrs["shape"] = np.array([mpi_size], dtype=np.uint64)

    for rank in np.arange(mpi_size):
        # each MPI rank would write its part independently
        # numParticles: number of particles in this patch
        particlePatches['numParticles'][rank] = globalNumParticles / mpi_size
        # numParticlesOffset: offset within the one-dimensional records where
        #                     the first particle in this patch is stored
        particlePatches['numParticlesOffset'][rank] = rank*globalNumParticles / mpi_size
        # offset and extent in the grid
        # example: 1D domain decompositon of 3D simulation along the first axis
        # 1st dimension spatial offset
        particlePatches['offset/x'][rank] = rank * grid_layout[0] / mpi_size
        particlePatches['extent/x'][rank] = grid_layout[0] / mpi_size


def main():
    # Open an exemple file
    f = h5.File("example.h5", "w")

    # Setup the root attributes for iteration 0
    setup_root_attr(f)

    # Setup basepath
    setup_base_path(f, iteration=0)
    
    # Write the field records
    write_meshes(f, iteration=0)

    # Write the particle records
    write_particles(f, iteration=0)

    # Close the file
    f.close()
    print("File example.h5 created!")


if __name__ == "__main__":
    main()
