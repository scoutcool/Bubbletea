

import setuptools
from os import path

VERSION = "0.0.7"
NAME="BubbleTea-py"

DESCRIPTION = "BubbleTea enables developers to quickly build any data applications on the emerging Web3 infrastructure."
LONG_DESCRIPTION = open("README.md", "rt").read()
LONG_DESCRIPTION = ""
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    LONG_DESCRIPTION = f.read()


# import sys
# try:
#     from pipenv.project import Project
#     from pipenv.utils import convert_deps_to_pip
# except:
#     exit_msg = (
#         "pipenv is required to package Streamlit. Please install pipenv and try again"
#     )
#     sys.exit(exit_msg)

# pipfile = Project(chdir=False).parsed_pipfile
# requirements = convert_deps_to_pip(pipfile["packages"].copy(), r=False)


setuptools.setup(
    name=NAME,
    version=VERSION,
    author="Supermax Tech.",
    author_email="hello@scout.cool",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/scout-cool/BubbleTea",
    # packages=['bubbletea-py'],
    # package_dir={'bubbletea-py': './'},
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        'streamlit==0.87.0','graphql-core==3.1.5', 'st-flashcard==0.0.5', 'python-dotenv==0.18.0', 'streamlit-aggrid==0.2.1'
    ],
    entry_points={
        'console_scripts': ['bubbletea = bubbletea.cli:run']
    },
    python_requires=">=3.6",
)
