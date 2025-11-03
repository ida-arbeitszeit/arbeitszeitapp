Hosting
=======

This application is designed to be self-hosted. The `IDA github organization <https://github.com/ida-arbeitszeit>`_ 
provides a repository that helps with hosting. If you are a community or organization that wants to host this application, 
feel free to contact IDA (`gruppe_arbeitszeit@riseup.net <mailto:gruppe_arbeitszeit@riseup.net>`_) for help.

Configuration of the web server
-------------------------------

The application needs to be configured to function properly. This is
done via a configuration file. When starting ``arbeitszeitapp`` it
looks for configuration files in the following locations from top to
bottom. It loads the first configuration file it finds:

* Path set in ``ARBEITSZEITAPP_CONFIGURATION_PATH`` environment variable
* ``/etc/arbeitszeitapp/arbeitszeitapp.py``

The configuration file must be a valid python script.  Configuration
options are set as variables on the top level. The following
configuration options are available:

.. include:: config_options_GENERATED.rst
