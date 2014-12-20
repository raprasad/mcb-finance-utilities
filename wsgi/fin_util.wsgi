import os
import sys

sys.stdout = sys.stderr     # send print statements to the apache logs

prod_paths = ['/var/webapps/django/mcb-finance-utilities'\
    , '/var/webapps/django/mcb-finance-utilities/finance_utilities']

for p in prod_paths:
    if os.path.isdir(p): 
        sys.path = [p] + sys.path
        # sys.path.append(p)

os.environ['DJANGO_SETTINGS_MODULE'] = 'finance_utilities.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

