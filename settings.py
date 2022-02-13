"""
To apply these settings, you have to restart Flask.
"""
# Directories
DATA_DIRECTORY = 'data'
DOCUMENT_DIRECTORY = 'docs'
INDEX_ODS = 'index.ods'
# TEMPLATE_DIRECTORY = 'templates'
# Files
BASE_TEMPLATE = 'base.html'
FRONT_SLUG = '~'
SLUG_404 = '!404'
MENU_INCLUDE_FRONT_NAME = True
MENU_FRONT_NAME_SEPARATOR = ' | '
DOC_CONTAINER_ID = 'legalazy-content'
KEEP_DOCUMENT_STYLES = True
# drop document styles for these types
#   application/json
KEEP_DOCUMENT_STYLES_APPLICATION_JSON = False
# Parse the OpenDocument to find publicly available font families
AUTODETECT_EXTERNAL_FONTS = True
# 3rd party
GOOGLE_FONTS_PATTERN = "https://fonts.googleapis.com/css?family={}"
GOOGLE_FONTS_WHITESPACE = '+'
