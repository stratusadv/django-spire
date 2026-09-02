from __future__ import annotations

from django_spire.metric.domain.models import Domain, SubDomain


def create_test_domain(
    name: str = 'test_domain',
    description: str = 'test_domain_description',
    sub_domain_name: str = 'test_domain_sub_domain_name',
) -> Domain:

    return Domain.objects.create(
        name=name, description=description, sub_domain_name=sub_domain_name
    )


def create_test_subdomain(
    domain: Domain, name: str = 'subdomain_name', description: str = 'testing subdomain_description'
) -> SubDomain:

    return SubDomain.objects.create(domain=domain, name=name, description=description)
