from setuptools import setup, find_packages

setup(
    name='facebook_fetch',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4>=4.7.1,<5',
        'flask>=1.0.3,<2',
        'mechanize>=0.4.2,<1',
        'pylint>=2.3.1,<4',
        'pymongo>=3.8.0,<4',
        'pyotp>=2.2.7,<3',
    ],
)
