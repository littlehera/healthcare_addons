from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in healthcare_addons/__init__.py
from healthcare_addons import __version__ as version

setup(
	name="healthcare_addons",
	version=version,
	description="Add-on features for Frappe/ERPNext Healthcare",
	author="littlehera",
	author_email="villanuevahera@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
