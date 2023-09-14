#!/bin/bash

mkdir _pylint_reports
pylint --rcfile=.pylintrc --exit-zero --persistent=n --output-format=json:_pylint_reports/pylint_report.json,colorized --reports=yes $(git ls-files '*.py')
pylint-json2html -o _pylint_reports/pylint_report.html -e utf-8 _pylint_reports/pylint_report.json
