from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='spectrogram',
    version='0.0.7',
    python_requires='>3.4',
    description="Spectrogram (80MHz bandwidth) accelerator for LimeSDR",
    long_description=readme,
    author="Gaspar Karm",
    author_email='gkarm@live.com',
    url='https://github.com/gasparka/spectrogram',
    license="Apache Software License 2.0",
    keywords='spectrogram, fft, limesdr',
    scripts=['bin/spectrogram']
)
