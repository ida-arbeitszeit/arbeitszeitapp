import os

from hypothesis import settings

settings.register_profile("default", max_examples=10)
settings.register_profile("ci", max_examples=1000)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))
