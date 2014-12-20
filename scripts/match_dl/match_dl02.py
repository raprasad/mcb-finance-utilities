
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
from hcom_reconcile.models import RequisitionEmail, RequisitionLineItem, PurchaseOrderEmail, PurchaseOrderLineItem
from common.msg_util import *

import xlrd
import re
from decimal import Decimal

CATEGORY_PAYMENTS = 'Payments'
CATEGORY_PURCHASE_ORDER = 'Purchase Invoices'
FREIGHT_ORDER = 'freight'
class DetailedListing:
    col_names = ['journal_category', 'batch_name', 'journal_header', 'transaction_line_description', 'fund_distribution', 'object_code', 'description', 'id_reference_number', 'amount', 'date', 'reconciled', 'year_logic', 'type', 'fund_subact', 'fund_title', 'fund_status', 'tub', 'org', 'fund', 'activity', 'subactivity', 'root', 'object_category', 'object_description', 'adi_journal_line_description', 'adi_journal_dff_description']
    date_attrs = ['date']
    
    def __init__(self, xls_row):
        if xls_row is None:
             raise Exception('xls_row is None')
        
        self.po_order_number = None
        self.purchase_order_object = None
        self.is_po_order = False
        
        self.load_data(xls_row)
    
    def load_data(self, xls_row):
        if xls_row is None:
            return
        
        if not len(xls_row) == len(self.col_names):
            raise Exception('Wrong number of values.  Expected [%s], received [%s]' % (len(self.col_names), len(xls_row) ))
                    
        for idx, attr_name in enumerate(self.col_names):
            val = xls_row[idx]  #.value
            val_class_name = val.__class__.__name__
            print '\n(%s) [%s]->[%s] %s' % (idx, attr_name, val, val.__class__.__name__)
            
            if attr_name in self.date_attrs and val is not None and re.match('\d{2}/\d{2}/\d{2}', str(val)):
                mth = int(val[0:2])
                day_num = int(val[3:5])
                yr = int(val[6:8])
                val_fmt = date(year=yr, month=mth, day=day_num)
            elif attr_name == 'amount' and val is not None:
                try:
                    val_fmt = Decimal(str(val))
                except:
                    val_fmt = Decimal('0')
            elif val is None:
                val_fmt = ''
            elif val_class_name == 'float':
                val_fmt = str(int(val)).encode('ascii', 'ignore')
            else:
                val_fmt = val.encode('ascii', 'ignore')
                if val_fmt == '':
                    val_fmt = None
                else:
                    val_fmt = val_fmt.strip()
                    
            print '[%s] -> [%s]' % (attr_name, val_fmt)
            self.__dict__.update({ attr_name : val_fmt })
           
        if self.journal_category in [ CATEGORY_PAYMENTS, CATEGORY_PURCHASE_ORDER] and not self.is_freight_order():
            self.is_po_order = True
            self.pull_purchase_order()
        
        print 'row loaded'
    
    def match_purchase_order_to_database(self):
        if not self.is_po_order:
            return False
            
        # match the po
        try:
            self.purchase_order_object = PurchaseOrderEmail.objects.get(purchase_order_num=self.po_order_number)
            print 'PO Match!'   
            return True 
        except PurchaseOrderEmail.DoesNotExist:
            return False

        return False
    
    def get_expense_code(self):
        if self.fund_distribution and self.object_code:
            ec = '%s.%s%s' % (self.fund_distribution[0:9] , self.object_code , self.fund_distribution[9:])
            return ec.replace('-', '.')
        return '?'
        
    def match_line_item(self):
        
        if (not self.purchase_order_object) or not self.purchase_order_object.requisition_email:
            return False
           
        """ 
        center_char_idx = len(self.transaction_line_description) / 2 
        if self.transaction_line_description[center_char_idx] == ';':
            li_search_desc = self.transaction_line_description[:center_char_idx].strip()
        else:
            li_search_desc = self.transaction_line_description.strip()
        """
        li_search_desc =  self.transaction_line_description.split(' ; ')[0].strip() 
        print 'li_search_desc: [%s]' % li_search_desc
        kwargs = {    'requisition' : self.purchase_order_object.requisition_email\
                    #, 'charge_account' : self.get_expense_code()\
                    , 'description__startswith' : li_search_desc\
                    #, 'amount' : self.amount
                    }
        print kwargs
        line_items = RequisitionLineItem.objects.filter(**kwargs)

        num_line_items = line_items.count()
        if num_line_items == 1:
            self.requisition_line_item = line_items[0]
            print 'RequisitionLineItem Match!'    
            return True
        elif num_line_items > 1:
            print '>>>>>>>>>>>>>>> Multiple match!!!'
        else:
            print 'no match'
        return False
        
    def is_freight_order(self):
        if self.transaction_line_description is None:
            return False

        desc_lowercase = self.transaction_line_description.lower()
        if desc_lowercase == FREIGHT_ORDER or desc_lowercase.startswith(FREIGHT_ORDER):
            return True
            
        return False
        
        
    def pull_purchase_order(self):
        if not self.is_po_order:
            return
        if self.id_reference_number is None:
            return 
            
        po_parts = self.id_reference_number.split()
        if len(po_parts)==0:
            return
            
        self.po_order_number = po_parts[0].strip()
    
    
    @staticmethod
    def create_detailed_listing(xls_row):
        if xls_row is None:
            return None
            
        if not len(xls_row) == len(DetailedListing.col_names):
            print 'Wrong number of values.  Expected [%s], received [%s]' % (len(DetailedListing.col_names), len(xls_row) )
            return None
            
        return DetailedListing(xls_row)
        
        
        
class DLReader:
    def __init__(self, fname):
        self.fname = "user-PO TEST 's PI's DOWNLOAD APRIL2013.xlsx"
        self.detail_listings = []
        self.load_data()
        
    def load_data(self):
        workbook = xlrd.open_workbook(fname)
        sheet = workbook.sheets()[0]
        first_data_row = 8
        num_rows = 0
        for i in xrange(sheet.nrows):
            num_rows += 1
            if num_rows >= first_data_row:
                dl = DetailedListing.create_detailed_listing(sheet.row_values(i))
                self.detail_listings.append(dl)
        
        
        po_listings = filter(lambda x: x.is_po_order, self.detail_listings )
        
        cnt =0 
        po_match_cnt = 0
        for po in po_listings:
            cnt += 1
            msgt('(%s) PO# %s' % (cnt, po.po_order_number))
            if po.match_purchase_order_to_database():
                po_match_cnt +=1
        
        line_item_match_cnt =0 
        po_match_listings = filter(lambda x: x.purchase_order_object, po_listings )
        po_cnt = 0
        for po in po_match_listings:
            po_cnt+=1
            msgt('(%s) try to match po: %s' % (po_cnt, po.po_order_number))
            if po.match_line_item():
                line_item_match_cnt+=1
        
        print '# detail listings', len(self.detail_listings)
        print '# PO listings', len(po_listings)
        print '# PO matches: %s [%s]' % (po_match_cnt, len(po_match_listings))
        print '# Line Item matches: %s' % (line_item_match_cnt)
        
        
if __name__=='__main__':    
    fname = "../data_dl/user-PO TEST 's PI's DOWNLOAD APRIL2013.xlsx"
    dlr = DLReader(fname)
