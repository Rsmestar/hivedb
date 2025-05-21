from setuptools import setup, find_packages

setup(
    name="hivedb",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pycryptodome>=3.10.1",
        "python-dotenv>=0.19.0",
    ],
    author="فريق HiveDB",
    author_email="info@hivedb.io",
    description="مكتبة Python لنظام قواعد بيانات HiveDB المستوحى من خلية النحل",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://hivedb.io",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
