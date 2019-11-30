import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = list(map(str.strip, f))

setuptools.setup(
    name="blueqat_classicalbit_backend",
    version="0.0.7",
    author="gyu-don",
    author_email="takumi.kt+blueqat@gmail.com",
    description="Blueqat backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gyu-don/blueqat-classicalbit-backend",
    license="Apache 2",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ]
)
