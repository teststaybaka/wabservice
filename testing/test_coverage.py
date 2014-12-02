from coverage import coverage

cov = coverage(branch=True, source=["../challenge_request_impl.py",
                                    "../challenge.py",
                                    "../views.py"])
cov.start()

from testing.challenge_request_unit_tests import *

suite = unittest.TestLoader().loadTestsFromTestCase(ChallengeRequestUnitTests)
unittest.TextTestRunner(verbosity=2).run(suite)

cov.stop()
cov.html_report(directory='coverage_report')