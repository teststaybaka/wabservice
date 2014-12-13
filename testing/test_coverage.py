from coverage import coverage

import unittest

file_list = [
    "../challenge_request.py",
    "../challenge.py",
    "../views.py",
    "../db_utils.py",
    "../account.py",
    "../facebook.py"]

cov = coverage(branch=True, source=file_list)
cov.start()

suite = unittest.TestLoader().discover('.', '*_test_cases.py')
unittest.TextTestRunner(verbosity=2).run(suite)

cov.stop()
percentage = cov.html_report(directory='coverage_report')
print('Overall coverage = {0}%'.format(percentage))

for file_name in file_list:
    result = cov.analysis2(file_name)
    executable_line_count = len(result[1])
    not_executed_line_count = len(result[3])
    percent = \
        1 - (float(not_executed_line_count) / float(executable_line_count))
    print('Coverage of {0}: {1}%'.format(file_name, percent * 100.0))