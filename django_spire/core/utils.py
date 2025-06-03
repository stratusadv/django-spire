def get_object_from_module_string(module_string):
    try:
        module_string, object_name = module_string.rsplit('.', 1)
        module = __import__(module_string, fromlist=[object_name])
    except ImportError:
        raise ImportError(f'Could not import module: {module_string}')

    return getattr(module, object_name)