{
  buildPythonPackage,
  postgresql,

  # python packages
  alembic,
  babel,
  psycopg2,
  email-validator,
  flask,
  flask-babel,
  flask-mail,
  flask-profiler,
  flask-restx,
  flask-talisman,
  flask-login,
  flask-wtf,
  matplotlib,
  parameterized,
  pytest,
  setuptools,
  sphinx,
  sphinx-rtd-theme,
}:
buildPythonPackage {
  pname = "arbeitszeitapp";
  version = "0.0.0";
  src = ../..;
  outputs = [
    "out"
    "doc"
  ];
  postPhases = [ "buildDocsPhase" ];
  format = "pyproject";
  buildInputs = [
    sphinx
    sphinx-rtd-theme
    parameterized
    babel
    setuptools
  ];
  propagatedBuildInputs = [
    alembic
    email-validator
    flask
    flask-babel
    flask-mail
    flask-talisman
    flask-login
    flask-restx
    flask-wtf
    matplotlib
  ];
  nativeBuildInputs = [
    pytest
    postgresql
    psycopg2
  ];
  buildDocsPhase = ''
    mkdir -p $doc/share/doc/arbeitszeitapp
    python -m sphinx -a $src/docs $doc/share/doc/arbeitszeitapp
  '';
  passthru.optional-dependencies = {
    profiling = [ flask-profiler ];
  };
  checkPhase = ''
    runHook preCheck

    # Run tests with SQLite.

    ARBEITSZEITAPP_TEST_DB=sqlite:////tmp/arbeitszeitapp_test.db pytest -x

    # Run tests with PostgreSQL.

    POSTGRES_DIR=$(mktemp -d)
    initdb -D $POSTGRES_DIR
    postgres -h "" -k $POSTGRES_DIR -D $POSTGRES_DIR &
    POSTGRES_PID=$!
    until createdb -h $POSTGRES_DIR; do echo "Retry createdb"; done

    ARBEITSZEITAPP_TEST_DB="postgresql:///?host=$POSTGRES_DIR" pytest -x

    kill $POSTGRES_PID

    runHook postCheck
  '';
}
