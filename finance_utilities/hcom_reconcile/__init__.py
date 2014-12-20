"""
from hcom_reconcile.po_email_loader import *
content = open('/Users/some-user/mcb-git/mcb-finance-utilities/scripts/hcom_email_check/blah.txt', 'r').read()

"""
"""

exit()
python manage.py shell

from hcom_reconcile.requisition_email_loader import RequisitionEmailMaker
from hcom_reconcile.hcom_email_parser import HCOMEmailParser
from hcom_reconcile.hcom_email_cleaner import HCOMEmailCleaner


#fname = '/Users/some-user/mcb-git/mcb-finance-utilities/scripts/hcom_email_check/input/email_ex_01_step1.eml'
fname = '/Users/some-user/projects/mcb-git/mcb-finance-utilities/scripts/hcom_email_check/input/email_ex_01_step1.eml'

print HCOMEmailCleaner.pull_html_from_email_file(fname)


#HCOMEmailParser.parse_email(fname)

"""

"""
import os, sys
pairs = { 'FW_ Standard Purchase Order _ ' : 'po_'\
    , 'FW__Purchase_Requisition_' : 'req_'\
    , 'FW__Standard_Purchase_Order__' : 'po_approval'\
    , 'po_approval' : 'po_approval_' \
    , '..eml' : '.eml' }
for fname in os.listdir('.'):
    for k, v in pairs.iteritems():
        if fname.startswith(k) or fname.endswith(k):
            os.rename(fname, fname.replace(k, v))
        #os.rename(fname, fname.replace(' ', '_'))
    #if not fname.endswith('.eml'):
    #    os.rename(fname, '%s.eml' % fname)

for fname in os.listdir('.'): fname
"""















