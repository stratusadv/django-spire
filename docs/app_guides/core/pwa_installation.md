# PWA Installation

> **Purpose:** Configure your Django Spire project as an installable Progressive Web App, enabling users to add it to their home screen on both iOS and Android/Chrome with native-like behaviour.

---

## Why PWA?

Installable web apps close the gap between a website and a native app. **PWA support in Django Spire** provides:

- A web manifest that tells browsers how to present your app when installed
- A built-in iOS install prompt with Safari-specific instructions
- A built-in Android/Chrome install button that hooks into the browser's `beforeinstallprompt` event
- Template blocks on both install elements so you can customise icons, text, and button styles without touching core files

---

## Quick Start

### 1. Create the Favicons Directory

Create a `django_spire/favicons/` directory inside your project's `static` or `staticfiles` directory:

```
your_project/
└── static/
    └── django_spire/
        └── favicons/
```

### 2. Create `manifest.json`

Add a `manifest.json` file to the favicons directory:

```json
{
    "name": "Your App Name",
    "short_name": "Your App",
    "description": "Your app description",
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

Update the fields to match your project. Ensure `src` values point to icon files that exist in the favicons directory.

### 3. Verify the Manifest Link

The Django Spire `base.html` includes the manifest link by default:

```html
--8<-- "docs/app_guides/core/templates/pwa_manifest_link.html"
```

If you are using a custom base template, add this line inside your `<head>` block.

---

## Core Concepts

### The iOS Install Element

Renders a button and modal that guide iOS users through the manual "Add to Home Screen" flow in Safari. Override the template to supply your app's icon and branding.

**Template path to override:**
```
templates/django_spire/auth/element/ios_app_install_element.html
```

**Available blocks:**

| Block | Description |
|---|---|
| `app_icon` | URL of the app icon shown in the modal |
| `alt_text` | Alt text for the app icon |
| `modal_trigger` | The button that opens the install instructions modal |

### The Android / Chrome Install Element

Listens for the browser's `beforeinstallprompt` event and shows an install button when the browser determines the app is installable. Override the template to customise the button.

**Template path to override:**
```
templates/django_spire/auth/element/android_and_chrome_app_install_element.html
```

**Available block:**

| Block | Description |
|---|---|
| `install_button` | The button shown to Android/Chrome users |

> **Note:** If you are not overriding `android_install_button.html` directly, ensure your custom install button element has the id `android-install-button` so the `beforeinstallprompt` JavaScript can find it.

---

## Main Operations

### Overriding the iOS Install Element

```html
--8<-- "docs/app_guides/core/templates/pwa_ios_override.html"
```

### Overriding the Android / Chrome Install Element

```html
--8<-- "docs/app_guides/core/templates/pwa_android_override.html"
```

Once both elements are in place, users will see an **Install App** button on the login page. Clicking it installs the project as a PWA on their device.


### Testing

#### Android / Chrome Install

1. Use your development laptop to install the app.
2. Ensure that the information, colors, images, and app icon is correct.
3. Visit your browser settings to uninstall it.


#### iOS Install

1. Comment out the `hidden` attribute in the `django_spire/auth/button/ios_install_button.html` file.
2. Click the install app button and ensure the information, colors, and images on the modal are correct.
3. Using an iOS device, install the app via the safari browser. Ensure the app icon is correct.
4. Uncomment the `hidden` attribute in the `django_spire/auth/button/ios_install_button.html` file.
