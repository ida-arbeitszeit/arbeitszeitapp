Hosting
=======

This application is designed to be self-hosted. The `IDA github organization <https://github.com/ida-arbeitszeit>` 
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
configuration options are available

.. py:data:: DEFAULT_USER_TIMEZONE

   The default timezone for users. This must be a valid timezone
   string as found in the `tz database`_.

   Example: ``DEFAULT_USER_TIMEZONE = "Europe/Berlin"``

   Default: ``"UTC"``

.. py:data:: ALEMBIC_CONFIGURATION_FILE

   Path to the alembic configuration. Alembic is used to manage
   database migrations. See the `alembic documentation`_ for further
   information.

.. py:data:: AUTO_MIGRATE
   
   Upgrade the database schema if changes are detected.

   Example: ``AUTO_MIGRATE = True``

   Default: ``False``

.. py:data:: FORCE_HTTPS

   This option controls whether the application will allow unsecure
   HTTP trafic or force a redirect to an HTTPS address.

   Example: ``FORCE_HTTPS = False``

   Default: ``True``

.. py:data:: MAIL_PLUGIN_MODULE

   This option must be a python module path to the email plugin to be
   used.  By default a mock email service will be used that is
   intended for development purposes.

   The arbeitszeitapp provides a very basic mechanism for sending
   emails synchronously via SMTP. This plugin is found in the
   ``arbeitszeit_flask.mail_service.smtp_mail_service`` module.

.. py:data:: MAIL_PLUGIN_CLASS

   This option must be the class name of the email service found under
   ``MAIL_PLUGIN_MODULE``.  By default a mock email service will be
   used that is intended for development purposes.

   The arbeitszeitapp provides a very basic mechanism for sending
   emails synchronously via SMTP. The name of this class in
   ``SmtpMailService``

.. py:data:: MAIL_SERVER
   
   The hostname of the SMTP server used for sending emails.

.. py:data:: MAIL_PORT
   
   Port of the SMTP server used to send emails.

   Default: ``25``

.. py:data:: MAIL_USERNAME
   
   The username required to log in to the ``SMTP`` server for sending emails.

.. py:data:: MAIL_PASSWORD
   
   The password required to log in to the ``SMTP`` server for sending emails.

.. py:data:: MAIL_DEFAULT_SENDER
   
   The sender address used for outgoing emails.

.. py:data:: MAIL_ADMIN

   The email address of the app administrator. Users may use this email 
   address to contact the administrator.

.. py:data:: SECRET_KEY
   
   A password used for protecting agains Cross-site request forgery
   and more. Setting this option is obligatory for many security
   measures.

.. py:data:: SECURITY_PASSWORD_SALT
   
   This option is used when encrypting passwords. Don't lose it.

.. py:data:: SERVER_NAME
   
   This variable tells the application how it is addressed. This is
   important to generate links in emails it sends out.

   Example: ``SERVER_NAME = "arbeitszeitapp.cp.org"``

.. py:data:: SQLALCHEMY_DATABASE_URI
   
   The address of the database used for persistence.

   Default: ``"sqlite:////tmp/arbeitszeitapp.db"``

   Example: ``SQLALCHEMY_DATABASE_URI = "postgresql:///my_data"``

.. py:data:: ALLOWED_OVERDRAW_MEMBER
   
   This integer defines how far members can overdraw their account in hours.
   Set to ``"unlimited"`` to allow unlimited overdraw.

   Default: ``0``

.. py:data:: ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION
   
   This integer defines the "relative deviation" from the ideal account balance of zero
   that is still deemed acceptable, expressed in percent and calculated 
   relative to the expected transfer value of this account.

   Example: Company XY has an absolute deviation of minus 1000 hours on its account for means
   of production (PRD account). Because it has filed plans with total costs for means of 
   production of 10000 hours (=the sum of expected transfer value), 
   its relative deviation is 10%.

   Unacceptable high deviations might get labeled as such or highlighted by the application.

   Default: ``33``


.. _alembic documentation: https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
.. _tz database: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
