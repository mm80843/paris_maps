from setuptools import setup 

exec(open('pypama/version.py').read())

setup(
  name = 'pypama',         # How you named your package folder (MyLib)
  packages = ['pypama'],   # Chose the same as "name"
  version = __version__,      # Start with a small number and increase it with every change you make
  license='gpl-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Code to find best explorations in Paris',   # Give a short description about your library
  author = 'Luc Jonveaux',                   # Type in your name
  author_email = 'luc.jonveaux@mottmac.com',      # Type in your E-Mail
  long_description=open('Readme.md').read(),
  long_description_content_type='text/markdown',
  url = 'https://github.com/mm80843/paris_maps/',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/mm80843/paris_maps/',    # I explain this later on
  keywords = ['paris', 'maps'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'osmnx','networkx'
          ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Science/Research',      # Define that your audience are developers
        'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  zip_safe=False,
  include_package_data=False,
)