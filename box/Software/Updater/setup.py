from setuptools import setup

setup(name='updater',
      version='0.1',
      description='Install opq box updater',
      author='Evan Hataishi',
      author_email='evanhata@hawaii.edu',
      license='MIT',
      scripts={'box_updater.py': ['*']},
      data_files=[('/etc/opq/', ['updater_config.json'])],
      install_requires=['python-crontab']
      )
