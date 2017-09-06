from setuptools import setup, find_packages


setup(name='dsputil',
    version='0.1',
    description='Utilities for working with the OPQ STM32',
    author='Sergey Negrashov',
    author_email='sin8 at hawaii dot edu',
    url='https://github.com/openpowerquality/opqbox2',
    packages=find_packages(),
    include_package_data=True,
    scripts=['dsputil/flashdsp', 'dsputil/resetdsp'],
    install_requires=[
        "RPI.GPIO",
    ],
)
