from setuptools import build_meta as _orig

from build_support import translations


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    return _orig.prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    translations.compile_messages()
    return _orig.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    return _orig.build_sdist(sdist_directory, config_settings)


def get_requires_for_build_wheel(self, config_settings=None):
    return _orig.get_requires_for_build_wheel(config_settings)


def get_requires_for_build_sdist(self, config_settings=None):
    return _orig.get_requires_for_build_sdist(config_settings)
