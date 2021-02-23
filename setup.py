#!/usr/bin/env python3

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()


setup(
    name='telemetrix-rpi-pico',
    packages=['telemetrix_rpi_pico'],
    install_requires=['pyserial'],

    version='0.2',
    description="Remotely Control And Monitor A Raspberry Pi Pico",
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Alan Yorinks',
    author_email='MisterYsLab@gmail.com',
    url='https://github.com/MrYsLab/telemetrix-rpi-pico',
    download_url='https://github.com/MrYsLab/telemetrix-rpi-pico',
    keywords=['telemetrix', 'Raspberry_Pi_Pico', 'Protocol', 'Python'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

