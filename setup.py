from setuptools import setup

with open("./README.md","r") as f:
	long_description = f.read()

setup(
	name="dataspace-downloader",
	version="0.0.10",
	description="A class to download a massive amount of Sentinel products.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/carlosmartinezvillar/dataspace-downloader",
	author="C.I. Martinez-Villar",
	author_email="cimartinezvillar@gmail.com",
	license="MIT",
	classifiers=[
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3.10",
		"Operating System :: OS Independent",
	],
	install_requires=["pyyaml >= 5.3", "requests"],
	extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.10",	
	)