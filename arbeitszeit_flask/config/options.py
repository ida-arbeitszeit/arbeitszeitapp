from dataclasses import dataclass, field


@dataclass
class ConfigOption:
    name: str
    converts_to_types: tuple[type, ...]
    description_paragraphs: list[str] = field(default_factory=list)
    example: str = ""
    default: str = ""

    def __hash__(self) -> int:
        return hash(self.name)


CONFIG_OPTIONS = [
    ConfigOption(
        name="DEFAULT_USER_TIMEZONE",
        converts_to_types=(str,),
        description_paragraphs=[
            "The default timezone for users. This must be a valid timezone string as found in the tz database."
        ],
        example='DEFAULT_USER_TIMEZONE = "Europe/Berlin"',
        default='"UTC"',
    ),
    ConfigOption(
        name="ALEMBIC_CONFIG",
        converts_to_types=(str,),
        description_paragraphs=[
            "Path to the alembic configuration. Alembic is used to manage database migrations. See the alembic documentation for further information.",
            'The target database for migrations is set via the "sqlalchemy.url" option in this file or via the ALEMBIC_SQLALCHEMY_DATABASE_URI environment variable.',
        ],
    ),
    ConfigOption(
        name="AUTO_MIGRATE",
        converts_to_types=(bool,),
        description_paragraphs=[
            "Upgrade the database schema if changes are detected on startup. If auto migration is not activated, you need to run database migrations manually via the ``alembic`` command line tool."
        ],
        example="AUTO_MIGRATE = True",
        default="False",
    ),
    ConfigOption(
        name="FORCE_HTTPS",
        converts_to_types=(bool,),
        description_paragraphs=[
            "This option controls whether the application will allow unsecure HTTP trafic or force a redirect to an HTTPS address."
        ],
        example="FORCE_HTTPS = False",
        default="True",
    ),
    ConfigOption(
        name="MAIL_PLUGIN_MODULE",
        converts_to_types=(str,),
        description_paragraphs=[
            "This option must be a python module path to the email plugin to be used. By default flask-mail is used. Other plugins can be found in the ``arbeitszeit_flask/mail_service`` directory.",
        ],
        default="arbeitszeit_flask.mail_service.flask_mail_service",
    ),
    ConfigOption(
        name="MAIL_PLUGIN_CLASS",
        converts_to_types=(str,),
        description_paragraphs=[
            "This option must be the class name of the email service found under ``MAIL_PLUGIN_MODULE``. By default ``FlaskMailService`` is used."
        ],
        default="FlaskMailService",
    ),
    ConfigOption(
        name="MAIL_SERVER",
        converts_to_types=(str,),
        description_paragraphs=[
            "The hostname of the SMTP server used for sending emails."
        ],
    ),
    ConfigOption(
        name="MAIL_PORT",
        converts_to_types=(int,),
        description_paragraphs=[
            "The port number of the SMTP server used for sending emails."
        ],
        default="587",
    ),
    ConfigOption(
        name="MAIL_USERNAME",
        converts_to_types=(str,),
        description_paragraphs=[
            "The username used to authenticate with the SMTP server."
        ],
    ),
    ConfigOption(
        name="MAIL_PASSWORD",
        converts_to_types=(str,),
        description_paragraphs=[
            "The password used to authenticate with the SMTP server."
        ],
    ),
    ConfigOption(
        name="MAIL_DEFAULT_SENDER",
        converts_to_types=(str,),
        description_paragraphs=["The sender address used for outgoing emails."],
    ),
    ConfigOption(
        name="MAIL_ADMIN",
        converts_to_types=(str,),
        description_paragraphs=[
            "The email address of the administrator for the application. Users may use this email address to contact the administrator."
        ],
    ),
    ConfigOption(
        name="MAIL_USE_TLS",
        converts_to_types=(bool,),
        description_paragraphs=[
            "Whether to use TLS when connecting to the SMTP server."
        ],
        default="True",
    ),
    ConfigOption(
        name="MAIL_USE_SSL",
        converts_to_types=(bool,),
        description_paragraphs=[
            "Whether to use SSL when connecting to the SMTP server."
        ],
        default="False",
    ),
    ConfigOption(
        name="SECRET_KEY",
        converts_to_types=(str,),
        description_paragraphs=[
            "A password used for protecting against Cross-site request forgery and more. Setting this option is obligatory for many security measures."
        ],
    ),
    ConfigOption(
        name="SECURITY_PASSWORD_SALT",
        converts_to_types=(str,),
        description_paragraphs=[
            "This option is used when encrypting passwords. Don't lose it."
        ],
    ),
    ConfigOption(
        name="SERVER_NAME",
        converts_to_types=(str,),
        description_paragraphs=[
            "This variable tells the application how it is addressed. This is important to generate links in emails it sends out."
        ],
        example='SERVER_NAME = "arbeitszeitapp.cp.org"',
    ),
    ConfigOption(
        name="SQLALCHEMY_DATABASE_URI",
        converts_to_types=(str,),
        description_paragraphs=[
            "The address of the database used for persistence. The application has been tested with PostgreSQL and SQLite databases."
        ],
        default='"sqlite:////tmp/arbeitszeitapp.db"',
        example='SQLALCHEMY_DATABASE_URI = "postgresql:///my_data"',
    ),
    ConfigOption(
        name="ALLOWED_OVERDRAW_MEMBER",
        converts_to_types=(int, str),
        description_paragraphs=[
            "The maximum allowed overdraw limit for members in hours (integer). Set to ``unlimited`` to allow unlimited overdraw."
        ],
        default="0",
    ),
    ConfigOption(
        name="ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION",
        converts_to_types=(int,),
        description_paragraphs=[
            'This integer defines the "relative deviation" from the ideal account balance of zero that is still deemed acceptable, expressed in percent and calculated relative to the expected transfer value of this account.',
            "Example: Company XY has an absolute deviation of minus 1000 hours on its account for means of production (PRD account). Because it has filed plans with total costs for means of production of 10000 hours (=the sum of expected transfer value), its relative deviation is 10%.",
            "Unacceptable high deviations might get labeled as such or highlighted by the application.",
        ],
        default="33",
    ),
]
