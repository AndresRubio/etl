import unittest

from monitoring import log
from test_etl import EtlModuleTests


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(EtlModuleTests))
    return test_suite


if __name__ == '__main__':
    log.info("--- NEXT UNIT TESTS---")

    unittest.TextTestRunner().run(suite())

    log.info("--- NEXT UNIT TESTS END ---")
