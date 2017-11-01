from setuptools import setup

setup(name='updater',
      version='0.1',
      description='Install opq updater',
      author='Evan Hataishi',
      author_email='evanhata@hawaii.edu',
      license='MIT',
      scripts={'updater.py': ['*']},
      data_files=[('config.json'), ('requirements.txt')]
      )
