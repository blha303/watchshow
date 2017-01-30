from setuptools import setup

desc = "A tool that gets a video url for a given show name, season number and episode number"

setup(
    name = "watchshow",
    packages = ["watchshow"],
    install_requires = ["requests", "beautifulsoup4"],
    entry_points = {
        "console_scripts": ["watchshow = watchshow.watchshow:main"]
        },
    version = "1.1.0",
    description = desc,
    long_description = desc,
    author = "Steven Smith",
    author_email = "stevensmith.ome@gmail.com",
    license = "MIT",
    url = "https://github.com/blha303/watchshow",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        ]
    )
