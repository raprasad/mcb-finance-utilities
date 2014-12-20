
from datetime import date, datetime
import os, sys

if __name__=='__main__':
    p1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    p2 = os.path.join(p1, 'finance_utilities')
    for pth in [p1, p2]:
        if os.path.isdir(p1): 
            sys.path.append(pth)
    
    from finance_utilities import settings
    from django.core.management import setup_environ
    setup_environ(settings)
    from django.utils.encoding import smart_str, smart_unicode

from hcom_reconcile.requisition_email_loader import RequisitionEmailMaker
from hcom_reconcile.hcom_email_parser import HCOMEmailParser
from hcom_reconcile.hcom_email_cleaner import HCOMEmailCleaner
from hcom_reconcile.hcom_match_po import RecordMatcher
from hcom_reconcile.models import *#RequisitionEmail, RequisitionLineItem, PurchaseOrderEmail, PurchaseOrderLineItem
from common.msg_util import *

def match_po():
    po_cnt = 0
    for po in PurchaseOrderEmail.objects.filter(is_matched=False):
        #filter(purchase_order_num='PR000687472'):
        po_cnt+=1
        msgt('(%s) match attempt: %s' % (po_cnt, po))
        rm = RecordMatcher(po_record=po)

def run_test2(fname, cnt=None):
    #fname = '/Users/some-user/projects/mcb-git/mcb-finance-utilities/scripts/hcom_email_check/input/email_ex_01_step1.eml'
    hp = HCOMEmailParser.parse_email(fname, cnt)

def run_test(fname):
    #fname = '/Users/some-user/mcb-git/mcb-finance-utilities/scripts/hcom_email_check/input/email_ex_01_step1.eml'
    #fname = '/Users/some-user/projects/mcb-git/mcb-finance-utilities/scripts/hcom_email_check/input/email_ex_02_step1.eml'
    mail_file_content = HCOMEmailCleaner.pull_html_from_email_file(fname)
    requisition_num = '123'
    #print mail_file_content
    open('ztest.html', 'w').write(mail_file_content.encode('ascii', 'ignore'))
    requisition_email = RequisitionEmailMaker(requisition_num, '<html>%s</html>' % mail_file_content)
    requisition_email.pull_email_1()
    requisition_email.show_info_dict()
    requisition_email.make_requisition_obj()
    
def load_test_recs(dirname):    
    msgt('load: %s' % dirname)
    cnt = 0
    for fname in os.listdir(dirname):
        if fname.endswith('.eml') or fname.endswith('.emlx'):
            cnt+=1
            #if cnt ==15:
            run_test2(os.path.join(dirname, fname), cnt)

def unmatch_pos():
    for po in PurchaseOrderEmail.objects.all():
        po.requisition_email = None
        po.save()
        
def clear_all():
    print 'clearing all data...'
    PurchaseOrderLineItem.objects.all().delete()
    PurchaseOrderEmail.objects.all().delete()
    RequisitionLineItem.objects.all().delete()
    RequisitionEmail.objects.all().delete()
    for model_name in """HcomPersonName HcomCategory HcomSupplier HcomSite HcomUnit""".split():
        eval('%s.objects.all().delete()' % model_name)
    print 'DONE'
if __name__=='__main__':
    #clear_all()
    load_test_recs(dirname='../data5')
    #unmatch_pos()
    match_po()
    
    
#run_test2('../data/po_approval___40000687077__has_been_approved.eml')
#load_test_recs(dirname='../data')
#load_test_recs(dirname='../data2')
#load_test_recs(dirname='../data3')
#load_test_recs(dirname='../data4')
#load_test_recs(dirname='../data5')
#unmatch_pos()
#match_po()
    
"""
import os
for fname in os.listdir('.'):
    if fname.startswith('FW_'):
        if not fname.endswith('.eml'):
            os.rename(fname, '%s.eml' % fname)

"""
    
    
    
    
    
    
    
    
    
    
    