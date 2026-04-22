from __future__ import annotations


ARCHIVE_EXTENSIONS = frozenset({
    '7z',
    'bz2',
    'gz',
    'rar',
    'tar',
    'xz',
    'zip',
})

DOCUMENT_EXTENSIONS = frozenset({
    'csv',
    'doc',
    'docx',
    'epub',
    'ods',
    'odt',
    'pages',
    'pdf',
    'ppt',
    'pptx',
    'rtf',
    'txt',
    'xls',
    'xlsx',
})

EXECUTABLE_EXTENSIONS = frozenset({
    'app',
    'bat',
    'bin',
    'cmd',
    'com',
    'dll',
    'exe',
    'gadget',
    'inf',
    'jar',
    'msi',
    'msp',
    'pif',
    'ps1',
    'reg',
    'rgs',
    'scr',
    'sh',
    'vb',
    'vbs',
    'ws',
    'wsf',
})

FONT_EXTENSIONS = frozenset({
    'eot',
    'otf',
    'ttf',
    'woff',
    'woff2',
})

IMAGE_EXTENSIONS = frozenset({
    'avif',
    'bmp',
    'gif',
    'heic',
    'heif',
    'ico',
    'jpeg',
    'jpg',
    'png',
    'tiff',
    'webp',
})

MARKUP_EXTENSIONS = frozenset({
    'htm',
    'html',
    'mhtml',
    'svg',
    'xhtml',
    'xml',
})

MEDIA_EXTENSIONS = frozenset({
    'aac',
    'aiff',
    'avi',
    'flac',
    'flv',
    'm4a',
    'm4v',
    'mkv',
    'mov',
    'mp3',
    'mp4',
    'mpeg',
    'mpg',
    'ogg',
    'opus',
    'wav',
    'webm',
    'wma',
    'wmv',
})

SCRIPT_EXTENSIONS = frozenset({
    'cgi',
    'css',
    'js',
    'jsx',
    'php',
    'pl',
    'py',
    'rb',
    'ts',
    'tsx',
})

DEFAULT_BLOCKED_EXTENSIONS = EXECUTABLE_EXTENSIONS | MARKUP_EXTENSIONS | SCRIPT_EXTENSIONS
