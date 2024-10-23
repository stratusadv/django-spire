from setuptools import find_packages, setup

from django_spire import __version__

setup(
    name="django-spire",
    version=__version__,
    description="Django framework for high observability web applications",
    long_description=open("README.md").read(),
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
    keywords=["glue", "django", "backend", "frontend", "javascript", "active server pages"],
    author="Brayden Carlson, Nathan Johnson, Austin Sauer & Wesley Howery",
    author_email="info@stratusadv.com",
    url="https://github.com/stratusadv/django-spire",
    license="MIT",
    packages=find_packages(exclude=["docs"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "django>=5.1.2",
        "django-glue>=0.7.8",
        "dandy>=0.2.0",
    ]
)

