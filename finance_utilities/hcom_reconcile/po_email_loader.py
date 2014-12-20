from hcom_reconcile.models import *

from hcom_reconcile.hcom_email_cleaner import HCOMEmailCleaner
from datetime import datetime
from decimal import Decimal
import os, sys
from common.msg_util import *
from BeautifulSoup import BeautifulSoup as Soup
import re

class PurchaseOrderEmailReader:
    
    PO_EMAIL_PATTERN = r'Standard Purchase Order\s{1,3}(\w{2}\d{5,25})\s{1,3}has been approved'
    
    # Standard Purchase Order 40000686478 Amount: USD 100.85; Tax: USD 0.00.
    # Standard Purchase Order NR000645161 Amount: USD 1,270.00; Tax: USD 0.00.

    #PO_TOTAL_AMT_AND_TAX_PATTERN = r'Standard Purchase Order\s{1,3}\w{2}\d{5,25}\s{1,3}Amount:\s{1,3}USD\s{1,3}([\d|,]{1,10}\.\d{2});\s{1,3}Tax:\s{1,3}USD\s{1,3}(\d{1,7}\.\d{2})\.'
    
    PO_TOTAL_AMT_AND_TAX_PATTERN = r'Standard Purchase Order\s{1,3}\w{2}\d{5,25}\s{1,3}Amount:\s{1,3}USD\s{1,3}([\d|,]{1,10}\.\d{2});\s{1,3}Tax:\s{1,3}USD\s{1,3}([\d|,]{1,7}\.\d{2})\.'
    
    @staticmethod
    def pull_total_amount_and_tax(full_email_content):
        
        if re.search(PurchaseOrderEmailReader.PO_TOTAL_AMT_AND_TAX_PATTERN, full_email_content):
            total_amount = re.search(PurchaseOrderEmailReader.PO_TOTAL_AMT_AND_TAX_PATTERN, full_email_content).group(1)
            tax_amount = re.search(PurchaseOrderEmailReader.PO_TOTAL_AMT_AND_TAX_PATTERN, full_email_content).group(2)
            
            print 'total [%s] tax [%s]' % (total_amount, tax_amount)
            return (total_amount, tax_amount)
        return None
        
    email_to_object_map = {  'hcom_idnum' : 'ID'\
                        , 'from_name' : 'From'\
                        , 'to_name' : 'To'\
                        , 'total_amt' : 'total_amt'
                        , 'tax_amt' : 'tax_amt'
                        #, 'description' : 'Description'\
                        #, 'requisition_total' : 'Requisition Total'\
                        #, 'estimated_tax' : 'Estimated Tax'\
                        , 'sent_time' : 'Sent'\
                    }
    month_num_table = { 'jan':1, 'feb':2, 'mar' : 3, 'apr': 4, 'may': 5, 'jun' : 6\
                        ,'jul' : 7, 'aug' : 8, 'sep':9, 'oct':10, 'nov': 11, 'dec': 12\
                        }
    email2_line_item_attrs = """line item_number rev description uom quantity unit_price line_amount""".split()

    def __init__(self, purchase_order_num, html_source, total_amt, tax_amt):
        print 'OK! PurchaseOrderEmailMaker init'
        self.info_dict = { 'total_amt' : total_amt, 'tax_amt' : tax_amt}
        self.line_item_dicts = []
        
        self.html_source = html_source
        print 'source size: [%s]' % len(html_source)
        #self.purchase_order_num = purchase_order_num
        
        self.purchase_order_num = purchase_order_num

    
    def get_val_by_email_to_object_map(self, attr_name):
        return self.info_dict.get( self.email_to_object_map.get(attr_name, None), None )
      
        
    def load_line_items(self, requisition_obj):
        if requisition_obj is None:
            return
        
        for li_dict in self.line_item_dicts:
            self.load_single_item(requisition_obj, li_dict)
            
    def load_single_item(self, po_obj, li_dict):
        if po_obj is None or li_dict is None:
            return
        
        dashes()
        print li_dict
        dashes()
        print 'unit 1: [%s]' % li_dict.get('uom')
        print 'unit 2: [%s]' % HcomUnit.get_hcom_unit(li_dict.get('uom', 'unknown'))

        li_kwargs = {'purchase_order' : po_obj\
                , 'line_num' : int(li_dict.get('line', -1) )\
                , 'description' : li_dict.get('description')\
                , 'item_number' : li_dict.get('item_number')\
                , 'rev' : li_dict.get('rev')\
                , 'unit' : HcomUnit.get_hcom_unit(li_dict.get('uom', 'unknown'))\
                , 'quantity' : self.get_decimal_val(li_dict.get('quantity'))\
                
                , 'price' : self.get_decimal_val(li_dict.get('unit_price')) \
                , 'amount' : self.get_decimal_val(li_dict.get('line_amount')) \
        }
        for k, w in li_kwargs.iteritems():
            print '%s -> %s' % (k, w)
        try:
            rlitem = PurchaseOrderLineItem.objects.get(**li_kwargs)
            print 'PurchaseOrderLineItem already added'
        except:
            rlitem = PurchaseOrderLineItem(**li_kwargs)
            rlitem.save()
            print 'PurchaseOrderLineItem created:)'
        
    def get_decimal_val(self, val):
        if val is None:
            return None
        
        try:
            return Decimal(val.replace('USD','').replace(',','').strip())
        except:
            return None
            
    def make_purchase_order_obj(self):
       
        kwargs = { 'purchase_order_num' : self.purchase_order_num }
        
        # string attrs
        for attr in [ 'hcom_idnum']:
            kwargs.update( { attr : self.get_val_by_email_to_object_map(attr) } )

        # Names
        for attr in ['from_name', 'to_name']:
            val = self.get_val_by_email_to_object_map(attr)
            print val
            kwargs.update( { attr : HcomPersonName.get_hcom_person_name(val) } )


        # Money
        for attr in ['total_amt', 'tax_amt']:
            val = self.get_val_by_email_to_object_map(attr)
            if val is not None:
                kwargs.update( { attr : self.get_decimal_val(val) } )
        print kwargs

              
        # 03-Apr-2013 11:58:04
        # 'sent_time'
        # Time
        sent_val = self.get_val_by_email_to_object_map('sent_time')
        if sent_val is not None and len(sent_val.strip()) >= 20:
            mth_num = self.month_num_table.get(sent_val[3:6].lower(), '?')   # find month num for 'Apr', e.g. 4
            sent_time_val = sent_val.replace(sent_val[3:6], `mth_num`) # e.g. replace Apr with 4 
            sent_time_datetime = datetime.strptime(sent_time_val, '%d-%m-%Y %H:%M:%S')
            kwargs.update( { 'sent_time' : sent_time_datetime } )
            
        print kwargs
        
        kwargs.update( { 'email_html' : self.html_source } )
        
        try:
            po_email = PurchaseOrderEmail.objects.get(**kwargs)
            print 'already exists'
        except PurchaseOrderEmail.DoesNotExist:
            po_email = PurchaseOrderEmail(**kwargs)
            po_email.save()
            print 'saved'
        
        self.load_line_items(po_email)
        
    def show_info_dict(self):
        for k, v in self.info_dict.iteritems():
            print '[%s] -> [%s]' % (k, v)

        for li_dict in self.line_item_dicts:
            dashes()
            for k, v in li_dict.iteritems():
                print '[%s] -> [%s]' % (k, v)

    
    def pull_mail2_line_items_from_row(self, soup_tr_info):
        rkey = None
        rval = None
        line_item_dict = {}
        for idx, td_info in enumerate(soup_tr_info.findAll('td')):
            print '(%s) [%s][class:%s]' % (idx, td_info.text, td_info.text.__class__.__name__)
        
            rkey = self.email2_line_item_attrs[idx]
            line_item_dict.update({ rkey: td_info.text })        
            print '%s -> "%s"' % (rkey, td_info.text)
        self.line_item_dicts.append(line_item_dict)

        
    def pull_info_from_row(self, soup_tr_info, val_in_4th_col=False):
        # 3 <td>'s:
        #   1 - label/field
        #   2 - img for formatting
        #   3 - value
        #   4 - possible value
        rkey = None
        rval = None
        for idx, td_info in enumerate(soup_tr_info.findAll('td')):
            print '(%s) [%s][class:%s]' % (idx, td_info.text, td_info.text.__class__.__name__)
            if idx == 0:
                rkey = td_info.text
            elif (idx == 2 and not val_in_4th_col) or (idx == 3 and val_in_4th_col):
                rval = td_info.text
                if rkey is not None:
                    self.info_dict.update({ rkey: rval })  

    
    def pull_email_info(self):
        soup = Soup(self.html_source)    
        print 'pull email info'
        tbl_cnt = 0
        requisition_table_num = -100

        for soup_table in soup.findAll('table'):
            tbl_cnt+=1
            #msgt('table: %s' % tbl_cnt)
            for tr_idx, soup_tr in enumerate(soup_table.findAll('tr')):
                row_cnt = tr_idx + 1
                row_str = '[T:%s][R:%s]' % (tbl_cnt, row_cnt)
                msgt('table: %s' % row_str)
                print soup_tr
                dashes()
    
                if tbl_cnt==1 and row_cnt==2:   # (top level information)
                    msgt('START PARSE 1')
                    #info1_soup = soup_tr.findAll('table')
                    for info1_tbl_soup in soup_tr.findAll('table'):
                        for soup_tr_info in info1_tbl_soup.findAll('tr'):
                            self.pull_info_from_row(soup_tr_info, val_in_4th_col=True)
                            print soup_tr_info
                            dashes()
                    msgt('END PARSE 1')
                    #msgx('exit')
                elif tbl_cnt == 4 and row_cnt>=2:
                    msgt('-- start: LINE ITEM PARSE')
                    self.pull_mail2_line_items_from_row(soup_tr)
                    msgt('-- end: LINE ITEM PARSE')
    
             
 
if __name__=='__main__':
    #input_file = 'input/email_orig_html_doc.html'
    #laundered_fname = 'output/laundered.html'
    email_input_file = 'input/email_ex_01_step1.eml'
    HCOMEmailParser.parse_email(email_input_file)
