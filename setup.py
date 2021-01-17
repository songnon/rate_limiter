import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


INSTALL_REQUIRES = []

setuptools.setup(
    name="rate_limiter",
    version="0.0.1",
    author="Shenglong Zhang",
    author_email="songnon@gmail.com",
    description="HTTP request rate limiting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    package_data={'rate_limiter': ['*.json', '*.ini']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
