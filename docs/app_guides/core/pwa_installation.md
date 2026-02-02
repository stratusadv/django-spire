# Progressive Web App Installation

Learn the proces on how to use the Progressive Web App (PWA) functionality on a login authentication page.

### Step 1: Create a `django_spire/favicons/` directory in your `core/static` directory

This is where we will store the `manifest.json` file needed for the PWA system on our login page.

### Step 2 Create a `manifest.json` file in the favicons directory.

This will be used to store the related information needed for the PWA system.

#### Example:

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
