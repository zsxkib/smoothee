from setuptools import setup, find_packages

setup(
    name="smoothee",
    version="0.0.1",
    author="Sakib Ahamed",
    author_email="sakib@replicate.com",
    description="Video frame-interpolation Python package utilizing Replicate models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zsxkib/smoothee",
    packages=find_packages(),
    install_requires=[
        "tensorflow==2.8.0",
        "tensorflow-datasets==4.4.0",
        "tensorflow-addons==0.16.1",
        "absl-py==0.12.0",
        "gin-config==0.5.0",
        "parameterized==0.8.1",
        "mediapy==1.0.3",
        "scikit-image==0.19.1",
        "imageio[ffmpeg]",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9.12",
)
