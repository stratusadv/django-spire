def get_object_from_module_string(module_string):
    try:
        module_string, object_name = module_string.rsplit('.', 1)
        module = __import__(module_string, fromlist=[object_name])
    except ImportError:
        raise ImportError(f'Could not import module: {module_string}')

    return getattr(module, object_name)

def get_generic_type_args(generic_type, index=0):
    generic_type_args = generic_type.__orig_bases__[index]
    return generic_type_args