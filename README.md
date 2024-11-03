# django-spire

![django_spire](https://i.imgur.com/NsiXyOX.png)

`django_spire` is a modular framework designed to enhance observability and improve the development of Django web applications.


## Features
- **Modular Architecture**: Select and install only the modules you need.
- **Seamless Integration**: Works alongside your existing Django application without intrusive changes.
- **Customizable & Extensible**: Configure and extend modules to suit specific project requirements.


## Getting Started
```
pip install django_spire
```

Add `django_spire` to your Django project’s `INSTALLED_APPS`:

```
INSTALLED_APPS = [
    'django_spire',
    'django_spire.authentication',
    'django_spire.breadcrumb',
    'django_spire.comment',
    'django_spire.core',
    'django_spire.file',
    'django_spire.form',
    'django_spire.gamification',
    'django_spire.help',
    'django_spire.history',
    'django_spire.maintenance',
    'django_spire.notification',
    'django_spire.options',
    'django_spire.pagination',
    'django_spire.permission',
    'django_spire.search',
    'django_spire.user_account'
]
```

Select and configure the modules that best suit your requirements.


## Documentation

Please refer to our documentation for detailed setup, module configuration, and usage examples.


## Contributing

We welcome contributions! Please see our contributing guide for more details on how to get involved.
