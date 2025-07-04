from setuptools import setup, find_packages

requirements = [
    'tqdm',
    'requests',
]

setup(
    name="sat_download",
    version="1.0.0",
    author="Sergio Heredia",
    author_email="sergiohercar1@gmail.com",
    description=" A python library to download remote sensing data like Sentinel-2 or Landsat-8 using diferent APIs like Copernicus OData API.",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/Aouei/remote-sensing-satellite-downloader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
)