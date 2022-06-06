from setuptools import build_meta as _orig


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    import subprocess

    subprocess.run(["python", "setup.py", "compile_catalog"])
    return _orig.prepare_metadata_for_build_wheel(
        metadata_directory, config_settings=None
    )


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _orig.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    return _orig.build_sdist(sdist_directory, config_settings)


def get_requires_for_build_wheel(self, config_settings=None):
    return _orig.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(self, config_settings=None):
    return _orig.get_requires_for_build_sdist(config_settings) + ["flask-babel"]
