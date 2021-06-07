import setuptools
VERSION = "0.0.5"
long_description = 'HELLO WORLD '+VERSION

setuptools.setup(
    name="example-pkg-earlgrey",
    version=VERSION,
    author="Supermax Tech.",
    author_email="hello@scout.cool",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scout-cool/streamlit_flow",
    package_dir={"": "lib"},
    packages=setuptools.find_packages(where="lib"),
    install_requires=[
        'streamlit','graphql-core'
    ],
    entry_points={
        'console_scripts': ['earlgrey = earlgrey.cli:run']
    },
    python_requires=">=3.6",
)