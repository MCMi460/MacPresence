# Made by Deltaion Lee (MCMi460) on GitHub
import setuptools

from pathlib import Path

directory = Path(__file__).parent
long_description = (directory / "README.md").read_text()

setuptools.setup(
    name="mac-presence",
    version="1.2.0",
    description="Discord Rich Presence wrapper for MacOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Deltaion Lee",
    author_email="32529306+MCMi460@users.noreply.github.com",
    url="https://github.com/MCMi460/MacPresence",
    packages=[
        "presence",
    ],
    package_data={},
    install_requires=[],
)
