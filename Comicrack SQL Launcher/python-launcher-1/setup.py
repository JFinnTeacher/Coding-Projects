from setuptools import setup, find_packages

setup(
    name='python-launcher',
    version='0.1.0',
    author='J Finn',
    author_email='your.email@example.com',
    description='A ComicRack and MySQL Launcher Application',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/python-launcher',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'mysql-connector-python',  # for MySQL interactions
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',  # Since this is Windows-specific
    ],
    python_requires='>=3.6',
)