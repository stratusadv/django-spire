class ServiceDescriptor:
    """
        Acts like a django objects manager.
        If an attribute you access on another object is actually a descriptor.
    """
    def __init__(self, service_cls):
        self._service_cls = service_cls

    def __get__(self, instance, owner):
        # When accessed through the class, instance == None
        target = instance if instance is not None else owner
        return self._service_cls(target)
