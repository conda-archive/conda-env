#!/bin/bash
# Install nose, nose-progressive, and watchdog
watchmedo shell-command -R -p "*.py" \
  -c "nosetests --with-progressive"
#  -c "nosetests --with-progressive -a'now'" #run only the single test marked 'now' by nose.plugins.attrib.attr
