from os.path import exists
from distutils.core import setup
import timewatch

setup(
  name = 'timewatch',
  packages = ['timewatch'],
  version = 'v0.0',
  description = 'A library automating worktime reports for timewatch.co.il',
  long_description=(open('README.md').read() if exists('README.md') else ''),
   entry_points='''
        [console_scripts]
        timewatch=timewatch:app
    ''',
)
