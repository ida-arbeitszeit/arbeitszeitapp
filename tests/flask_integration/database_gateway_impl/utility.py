"""
Utility functions useful for database tests.
"""

class Utility:
    
    @staticmethod
    def mangle_case(input: str) -> str:
        return input.upper() if input[0].islower() else \
                input.lower()


