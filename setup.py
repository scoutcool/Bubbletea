import setuptools
from os import path

VERSION = "0.0.17"
NAME="BubbleTea"
DESCRIPTION = "hello "+NAME
LONG_DESCRIPTION = "https://github.com/scout-cool/earlgrey"


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
        'streamlit','graphql-core', 'st-flashcard'
    ],
    entry_points={
        'console_scripts': ['bubbletea = bubbletea.cli:run']
    },
    python_requires=">=3.6",
)