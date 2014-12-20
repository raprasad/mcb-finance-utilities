import os, sys
import re

from requisition_email_loader import RequisitionEmailMaker
from po_email_loader import PurchaseOrderEmailReader
from hcom_email_cleaner import HCOMEmailCleaner
from finance_utilities.common.msg_util import *

class HCOMEmailParser:
    """
    Given an email file or contents of an email file, decide:
        (1) parse as a Requisition Email
        (2) parse as a Purchase Order Email
    """
    @staticmethod
    def parse_email(email_input_filename, cnt=None):
        if not os.path.isfile(email_input_filename):
            print 'file doesn\'t exist: [%s]' % email_input_filename
            return None
        print ''
        if cnt:
            msgt('(%s) process file: %s' % (cnt, email_input_filename))
        else:
            msgt('process file: %s' % email_input_filename)
        
        FULL_EMAIL_CONTENT = open(email_input_filename, 'r').read()
                
        if re.search(RequisitionEmailMaker.REQUISITION_EMAIL_PATTERN, FULL_EMAIL_CONTENT):
            requisition_num = re.search(RequisitionEmailMaker.REQUISITION_EMAIL_PATTERN\
                                        , FULL_EMAIL_CONTENT).group(1)
            print 'Type 1. requisition_num: %s' % requisition_num
            #return
            mail_file_content = HCOMEmailCleaner.pull_html_from_email_content(FULL_EMAIL_CONTENT)
            #print mail_file_content
            #open('test.html', 'w').write(mail_file_content.encode('ascii', 'ignore'))
            requisition_email = RequisitionEmailMaker(requisition_num,  '<html>%s</html>' % mail_file_content)
            requisition_email.pull_email_info()
            requisition_email.show_info_dict()
            requisition_email.make_requisition_obj()
            
            
        elif re.search(PurchaseOrderEmailReader.PO_EMAIL_PATTERN, FULL_EMAIL_CONTENT):
            purchase_order_num = re.search(PurchaseOrderEmailReader.PO_EMAIL_PATTERN, FULL_EMAIL_CONTENT).group(1)
            print 'Type 2. purchase_order_num: %s' % purchase_order_num
                            
            mail_file_content = HCOMEmailCleaner.pull_html_from_email_content(FULL_EMAIL_CONTENT)
            purchase_amts = PurchaseOrderEmailReader.pull_total_amount_and_tax(mail_file_content)
            if purchase_amts is None:
                msgx('Purchase amounts not found in PO file: %s' % email_input_filename)
            
            print 'mail_file_content len: %s' % len(mail_file_content)
            
            po_kwargs = { 'purchase_order_num' : purchase_order_num\
                            , 'html_source' : '<html>%s</html>' % mail_file_content\
                            , 'total_amt' : purchase_amts[0]
                            , 'tax_amt' : purchase_amts[1]
                            }
            po_email = PurchaseOrderEmailReader(**po_kwargs)
            po_email.pull_email_info()
            po_email.show_info_dict()
            po_email.make_purchase_order_obj()
            #sm = SoupMaker(mail_file_content, **{ 'purchase_order_num' : purchase_order_num })
            #sm.pull_email_2()
            #sm.show_info_dict()
            #print 'email type 2'
        else:
            print 'unknown email type'
