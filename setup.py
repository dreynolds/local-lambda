import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="local_lambda",
    description="Simple mechanism for running lambdas locally for testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    install_requires=[
        "jsonschema==3.2.0",
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    scripts=[
        "src/scripts/local_lambda",
        "src/scripts/call_command.py",
    ],
    url="https://github.com/dreynolds/local-lambda",
    author="David Reynolds",
    author_email="david@reynoldsfamily.org.uk",
)
