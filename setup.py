from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requires = [
        line.strip()
        for line in f.read().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

setup_args = dict(
    name="dano_leaderboard",
    version="0.0.1",
    packages=find_packages(),
    author="Søren Vejlgaard Holm",
    author_email="soren@vholm.dk",
    install_requires=requires,
    long_description_content_type="text/markdown",
    long_description=readme,
    license="Apache License 2.0",
)

if __name__ == "__main__":
    setup(**setup_args)
