import setuptools
from os import path

VERSION = "0.0.8"
NAME="Earlgrey"
DESCRIPTION = "hello "+NAME
LONG_DESCRIPTION = NAME 
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
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
    name="example-pkg-earlgrey",
    version=VERSION,
    author="Supermax Tech.",
    author_email="hello@scout.cool",
    description="A small example package",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/scout-cool/streamlit_flow",
    package_dir={"": "lib"},
    packages=setuptools.find_packages(where="lib"),
    # install_requirements=requirements,
    install_requires=[
        'streamlit','graphql-core'
    ],
    entry_points={
        'console_scripts': ['earlgrey = earlgrey.cli:run']
    },
    python_requires=">=3.6",
)