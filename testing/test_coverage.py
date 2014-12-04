from coverage import coverage

cov = coverage(branch=True, source=[
    "../challenge_request_impl.py",
    "../challenge.py",
    "../views.py"])
cov.start()

from testing.unit_test_cases import *

suite = unittest.TestLoader().loadTestsFromName(
    'unit_test_cases')
unittest.TextTestRunner(verbosity=2).run(suite)

cov.stop()
cov.html_report(directory='coverage_report')