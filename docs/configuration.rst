Configuration of the web server
===============================

The app needs some configuration to properly function. Most of the
configuration should be done via process environment variables, or
"env vars" for short.

``ARBEITSZEIT_APP_SERVER_NAME=https://your.server.org/path/to/app``

This variable tells the application how it is addressed. This is
important to generate links in emails it sends out.
