from setuptools import setup
from xliff_converter import __version__

with open('Readme.rst', 'r', encoding='utf-8') as fo:
    long_descr = fo.read()

setup(
    name='py-xliff-converter',
    version=__version__,
    packages=['xliff_converter'],
    url='https://github.com/romanvm/py-xliff-converter',
    license='MIT',
    author='Roman Miroshnychenko',
    author_email='roman1972@gmail.com',
    description='Utilities for converting rich text markup files to XLIFF format',
    long_description=long_descr,
    install_requires=['nltk'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'html2xliff=xliff_converter.html2xliff:main',
            'xliff2html=xliff_converter.xliff2html:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic'
    ]
)
