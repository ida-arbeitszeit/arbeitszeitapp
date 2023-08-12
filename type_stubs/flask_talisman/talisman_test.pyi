import unittest
from _typeshed import Incomplete
from flask_talisman import ALLOW_FROM as ALLOW_FROM, DENY as DENY, NONCE_LENGTH as NONCE_LENGTH, Talisman as Talisman

HTTPS_ENVIRON: Incomplete

def hello_world(): ...
def with_nonce(): ...

class TestTalismanExtension(unittest.TestCase):
    app: Incomplete
    talisman: Incomplete
    client: Incomplete
    def setUp(self) -> None: ...
    def testDefaults(self) -> None: ...
    def testForceSslOptionOptions(self) -> None: ...
    def testForceXSSProtectionOptions(self) -> None: ...
    def testHstsOptions(self) -> None: ...
    def testFrameOptions(self) -> None: ...
    def testContentSecurityPolicyOptions(self) -> None: ...
    def testContentSecurityPolicyOptionsReport(self) -> None: ...
    def testContentSecurityPolicyNonce(self) -> None: ...
    def testDecorator(self): ...
    def testDecoratorForceHttps(self): ...
    def testForceFileSave(self) -> None: ...
    def testBadEndpoint(self) -> None: ...
    def testFeaturePolicy(self) -> None: ...
    def testPermissionsPolicy(self) -> None: ...
    def testDocumentPolicy(self) -> None: ...