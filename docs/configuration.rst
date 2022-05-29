Configuration of the web server
===============================

The application needs to be configured to function properly. This is
done via a configuration file. When starting ``arbeitszeitapp`` it
looks for configuration files in the following locations from top to
bottom. It loads the first configuration file it finds:

* Path set in ``ARBEITSZEITAPP_CONFIGURATION_PATH`` environment variable
* ``/etc/arbeitszeitapp/arbeitszeitapp.py``

The configuration file must be a valid python script.  Configuration
options are set as variables on the top level. The following
configuration options are available

.. py:data:: AUTO_MIGRATE
   Upgrade the database schema if changes are detected.

   Example: ``AUTO_MIGRATE = True``

   Default: ``False``

.. py:data:: FORCE_HTTPS
   This option controls whether the application will allow unsecure
   HTTP trafic or force a redirect to an HTTPS address.

   Example: ``FORCE_HTTPS = False``

   Default: ``True``

.. py:data:: MAIL_SERVER
   The server name of the SMTP server used to send mails.

.. py:data:: MAIL_PORT
   Port of the SMTP server used to send mails.

   Default: ``25``

.. py:data:: MAIL_USERNAME
   The username used to log in to the ``SMPT`` server used to send
   mail.

.. py:data:: MAIL_PASSWORD
   The password used to log in to the ``SMPT`` server used to send
   mail.

.. py:data:: MAIL_DEFAULT_SENDER
   The sender address used when sending out mail.

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
