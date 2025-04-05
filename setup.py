from setuptools import setup

readme_name = "README.md"
with open(readme_name) as fh:
    long_description = fh.read()
    
setup(
    name='pylexflp',
    version='0.1.3',    
    description='A Python Package for Fuzzy Linear Programming with the Lexicographic Method',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Fuzzy Optimization", "Fuzzy Linear Programming", "Fuzzy Set", "Fuzzy Number", "Operations Research"],
    url='https://github.com/bpcanedo/pylexflp',
    author='Boris Pérez-Cañedo',
    author_email='bpcanedo@gmail.com',
    packages=['pylexflp'],
    python_requires=">=3.7",
    install_requires=['pulp>=2.6',
                      'scipy>=1.10.1',                     
                      ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English', 
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
