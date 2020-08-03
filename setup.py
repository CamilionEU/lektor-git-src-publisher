import ast
import io
import re

from setuptools import find_packages, setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

_description_re = re.compile(r"description\s+=\s+(?P<description>.*)")

with open("lektor_git_src_publisher.py", "rb") as f:
    description = str(
        ast.literal_eval(_description_re.search(f.read().decode("utf-8")).group(1))
    )

setup(
    author="Andrés",
    author_email="andres+cvs@camilion.eu",
    description=description,
    keywords="Lektor plugin",
    license="MIT",
    long_description=readme,
    long_description_content_type="text/markdown",
    name="lektor-git-src-publisher",
    packages=find_packages(),
    py_modules=["lektor_git_src_publisher"],
    url="https://github.com/CamilionEU/lektor-git-src-publisher",
    version="0.2.1",
    classifiers=[
        "Framework :: Lektor",
        "Environment :: Web Environment",
        "Environment :: Plugins",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "lektor.plugins": [
            "git-src-publisher = lektor_git_src_publisher:GitSrcPublisherPlugin"
        ]
    },
)
