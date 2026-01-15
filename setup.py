from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gen-db",
    version="1.0.0",
    author="Stephan Epp",
    author_email="hjstephan@gmail.com",
    description="Biological Network Database and Analysis Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hjstephan/gen",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Computer Science :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "networkx>=2.6.0",
        ],
    },
)
