from django_spire import __version__


def spire(request):
    return {
        'DJANGO_SPIRE_VERSION': __version__
    }
