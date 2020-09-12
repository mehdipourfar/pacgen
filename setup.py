from setuptools import setup


with open('README.md') as f:
    long_description = f.read()

setup(
    name='PacGen',
    version='0.1.3',
    packages=['pacgen'],
    license='MIT License',
    url='https://github.com/mehdipourfar/pacgen',
    scripts=['scripts/updatepac'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['PyYAML'],
)
