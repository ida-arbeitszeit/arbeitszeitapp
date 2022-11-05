{ buildPythonPackage, fetchPypi, rich, cloudpickle, pynvml, setuptools-scm }:
buildPythonPackage rec {
  pname = "scalene";
  version = "1.5.14";
  src = fetchPypi {
    inherit pname version;
    sha256 = "Uc6ag+RvGHn9l4L+tFmzJ5EzwA/0Wys06TxFyj9LN4M=";
  };
  propagatedBuildInputs = [ rich cloudpickle pynvml ];
  doCheck = false;
  buildInputs = [ setuptools-scm ];
}
