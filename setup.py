#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='droplogger',
      description='Logging application',
      url='https://github.com/goodevilgenius/droplogger',
      version='0.8.1',
      author='Dan Jones',
      author_email='danjones@goodevilgenius.org',
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'droplogger=droplogger.droplogger:main',
              'drop-a-log=droplogger.drop_a_log:main'
              ]
      },
      package_data={
            'droplogger.outputs': ['templates/*.tpl']
      },
      include_package_data=True
     )
