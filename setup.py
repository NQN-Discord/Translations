from setuptools import setup, find_packages


setup(
   name="translation",
   version="0.1.0",
   description="Translation files for NQN",
   author='Blue',
   url="https://nqn.blue/",
   packages=find_packages(),
   install_requires=["python-i18n", "TextToOwO", "ruamel.yaml==0.17.21", "unidecode", "regex"]
)
