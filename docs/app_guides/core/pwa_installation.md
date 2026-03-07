# Progressive Web App Installation

Follow this process to setup your project with Progressive Web App (PWA) support.

### Step 1: Create a `django_spire/favicons/` directory in your `static` or `static_files` directory

### Step 2: Create a `manifest.json` file in the favicons directory.

### Step 3: Copy and paste the content below into the `manifest.json` file.

This will be used to store the related information needed for the PWA system.

```json
{
    "name": "Django Spire Portal",
    "short_name": "Django Spire",
    "description": "Django Spire Portal",
    "icons": [
        {
            "src": "android-chrome-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "android-chrome-256x256.png",
            "sizes": "256x256",
            "type": "image/png"
        }
    ],
    "lang": "en",
    "orientation": "portrait",
    "theme_color": "#4cc8ee",
    "background_color": "#4cc8ee",
    "display": "fullscreen",
    "id": "/",
    "start_url": "/",
    "scope": "/"
}
```

### Step 4: Update the content in the `manifest.json` file to your project's specific details.

- Ensure that `src` points to the path to your installation icons
- Make sure that `<link rel="manifest" href="{% static 'django_spire/favicons/manifest.json' %}">` is included in your `base.html` file. 
(Included in Spire `base.html` by default)

### Step 5: Override IOS Element Template File

For the IOS PWA element you will need to override the template and extend the blocks with your projects respective information.
**Note**: If not directly overriding / changing the 
`django_spire/auth/button/ios_install_button.html`, ensure that your element is assigned the ID `ios-install-button`

#### Example:

```html title='templates/django_spire/auth/element/ios_app_install_element.html'
{% extends 'django_spire/auth/element/ios_app_install_element.html' %}

{% load static %}

{% block app_icon %}{% static 'core/favicon/android-chrome-192x192.png' %}{% endblock %}

{% block alt_text %}Stratus ADV{% endblock %}

{% block modal_trigger %}
    % include 'django_spire/auth/button/ios_install_button.html' with button_type='btn-app-primary-outlined' %
{% endblock %}
```

### Step 6: Override Android / Chrome Element Template File

If desired, override the android install button. **Note**: If not directly overriding / changing the 
`django_spire/auth/button/android_install_button.html`, ensure that your element is assigned the ID `android-install-button`

#### Example:

```html title='templates/django_spire/auth/element/android_and_chrome_app_install_element.html'
{% extends 'django_spire/auth/element/android_and_chrome_app_install_element.html' %}

{% block install_button %}
    % include 'django_spire/auth/button/android_install_button.html' with button_type='btn-app-primary-outlined' %
{% endblock %}
```

You should now see an `Install App` button on the login page that when clicked will install your project as a PWA!
