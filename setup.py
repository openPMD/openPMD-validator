from setuptools import setup


def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f.readlines()]


def read_readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='openPMD-validator',
    version='1.0.0',
    url='https://github.com/openPMD/openPMD-validator',
    # author=...,  # TODO
    # author_email=...,  # TODO
    # maintainer=...,  # TODO
    # maintainer_email=...,  # TODO
    license='ISC',
    install_requires=read_requirements(),
    description='Validator and examples for openPMD format',
    long_description=read_readme(),
    classifiers=[
        # 'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    py_modules=[
        'checkOpenPMD_h5',
        'createExamples_h5',
    ],  # TODO: should actually be put in a package
    entry_points={
        'console_scripts': [
            'openPMD_check_h5 = checkOpenPMD_h5:main',
            'openPMD_createExamples_h5 = createExamples_h5:main',
        ]
    },
)
