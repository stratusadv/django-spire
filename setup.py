from setuptools import find_packages, setup

from django_spire.constants import VERSION


with open('LICENSE.md', encoding="utf-8") as license_handle:
    license_file = license_handle.read()

with open('README.rst', encoding="utf-8") as readme_handle:
    readme_file = readme_handle.read()

setup(
    name="django-spire",
    version=VERSION,
    description="Django framework for high observability web applications",
    license=license_file,
    long_description=readme_file,
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "spire",
        "django",
        "backend",
        "frontend",
        "javascript",
        "active server pages"
    ],
    author="Austin Sauer, Brayden Carlson, Nathan Johnson & Wesley Howery",
    author_email="info@stratusadv.com",
    url="https://github.com/stratusadv/django-spire",
    packages=find_packages(
        exclude=["docs", "example", "example.*", "tests", "tests.*"]
    ),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "django>=5.1.2",
        "django-glue>=0.7.8",
        "dandy>=0.2.0",
    ],
    package_data={
        "": ["README.rst", "LICENSE.md", "CHANGELOG.md", "CONTRIBUTORS.md"],
        "django_spire": [
            "**/*.html",
            "**/*.css",
            "**/*.js",
            "**/*.png",
            "**/*.jpg"
        ],
    },
    exclude_package_data={
        "": ["*.db"],
        "example": ["*"],
        "tests": ["*"],
    },
)

