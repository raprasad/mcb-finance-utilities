import os, sys
from msg_util import *
import lxml.html
#from lxml.html import clean
from lxml.html import clean 
import re
from django.template.defaultfilters import removetags
from BeautifulSoup import BeautifulSoup as Soup

class SoupMaker:
    
    email1_line_item_attrs = """line description category supplier site charge_account distribution_level_notes unit quantity price_usd amount_usd""".split()
    email2_line_item_attrs = """line item_number rev description uom quantity unit_price line_amount""".split()

    def __init__(self, html_content, **kwargs):
        self.info_dict = {}
        self.line_item_dicts = []
        
        self.purchase_order_num = kwargs.get('purchase_order_num', None)
        if self.purchase_order_num is not None:  
            self.info_dict.update({'purchase_order_num': self.purchase_order_num})

        self.requisition_num = kwargs.get('requisition_num', None)
        if self.requisition_num is not None:  
            self.info_dict.update({'requisition_num': self.requisition_num})
        #self.html_content_filename = html_content_filename
        self.html_source = html_content
        #self.test_soup()
        
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

    def pull_line_items_from_row(self, soup_tr_info):
        rkey = None
        rval = None
        line_item_dict = {}
        for idx, td_info in enumerate(soup_tr_info.findAll('td')):
            print '(%s) [%s][class:%s]' % (idx, td_info.text, td_info.text.__class__.__name__)
            
            rkey = self.email1_line_item_attrs[idx]
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

    def pull_email_2(self):
        soup = Soup(self.html_source)    

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
                elif tbl_cnt == 4 and row_cnt==2:
                    msgt('START PARSE 2')
                    #info1_soup = soup_tr.findAll('table')
                    self.pull_mail2_line_items_from_row(soup_tr)
                    continue
                    for info1_tbl_soup in soup_tr.findAll('table'):
                        for idx, soup_tr_info in enumerate(info1_tbl_soup.findAll('tr')):
                            if idx == 0:  
                                continue # skip title row
                            self.pull_line_items_from_row(soup_tr_info)
                            print soup_tr_info
                            dashes()
                    msgt('END PARSE 2')
                    #return
    
                    
    def pull_email_1(self):
        soup = Soup(self.html_source)    
        
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
                if soup_tr.find('td').text == 'Requisition Lines' and requisition_table_num == -100:
                    requisition_table_num = tbl_cnt
                
                elif tbl_cnt==2 and row_cnt==1:   # (top level information)
                    msgt('START PARSE 1')
                    #info1_soup = soup_tr.findAll('table')
                    for info1_tbl_soup in soup_tr.findAll('table'):
                        for soup_tr_info in info1_tbl_soup.findAll('tr'):
                            self.pull_info_from_row(soup_tr_info)
                            print soup_tr_info
                            dashes()
                    msgt('END PARSE 1')
                elif (tbl_cnt == requisition_table_num +2) and row_cnt==1:
                    msgt('START PARSE 2')
                    #info1_soup = soup_tr.findAll('table')
                    for info1_tbl_soup in soup_tr.findAll('table'):
                        for idx, soup_tr_info in enumerate(info1_tbl_soup.findAll('tr')):
                            if idx == 0:  
                                continue # skip title row
                            self.pull_line_items_from_row(soup_tr_info)
                            print soup_tr_info
                            dashes()
                    msgt('END PARSE 2')
                    #return
                    
                #print 'tr: %s' % (soup_tr)
            
class EmailCleaner:

    @staticmethod
    def pull_html_from_email_file(fname):
        content = open(fname, 'r').read()
        idx = content.find('<html')
        if idx==-1:
            return None
        end_idx = content.find('</html>', idx+5)
        if end_idx==-1:
            return None
            
        html_content = content[idx:end_idx+7]
        
        # remove line breaks 
        strings_to_remove = ['=\r\n',  '<o:p>', '</o:p>']
        for to_remove in strings_to_remove:
            html_content = html_content.replace(to_remove, '')

        # remove <img ...> and <span...> tags
        html_content = removetags(html_content, 'p b img span')

        # remove extra attributes
        safe_attrs=clean.defs.safe_attrs
        clean.defs.safe_attrs=frozenset()
        cleaner = clean.Cleaner(safe_attrs_only=True)
            
        html_content = cleaner.clean_html(html_content)
            
        return html_content

"""
import re

po_pattern = r'Standard Purchase Order\s{1,3}(\w{2}\d{5,25})\s{1,3}has been approved'
po_string = 'Standard Purchase Order  NR000676902  has been approved'

m_obj = re.search(po_pattern, po_string)
if m_obj:
    print 'match: %s' % m_obj.group(1)


"""

class HCOMEmailParser:
    @staticmethod
    def parse_email(email_input_filename):
        content = open(email_input_filename, 'r').read()
        
        email_type_1_pattern = r'Purchase Requisition\s{1,3}(\d{5,25})\s{1,3}(has been approved|for)'
        email_type_2_pattern = r'Standard Purchase Order\s{1,3}(\w{2}\d{5,25})\s{1,3}has been approved'
        
        if re.search(email_type_1_pattern, content):
            requisition_num = re.search(email_type_1_pattern, content).group(1)
            print 'requisition_num: %s' % requisition_num
            #return
            mail_file_content = EmailCleaner.pull_html_from_email_file(email_input_file)
            sm = SoupMaker(mail_file_content, **{ 'requisition_num' : requisition_num })
            sm.pull_email_1()
            sm.show_info_dict()
        elif re.search(email_type_2_pattern, content):
            purchase_order_num = re.search(email_type_2_pattern, content).group(1)
            print 'purchase_order_num: %s' % purchase_order_num
            #return
            mail_file_content = EmailCleaner.pull_html_from_email_file(email_input_file)
            sm = SoupMaker(mail_file_content, **{ 'purchase_order_num' : purchase_order_num })
            sm.pull_email_2()
            sm.show_info_dict()
            print 'email type 2'
        else:
            print 'unknown email type'
              
if __name__=='__main__':
    #input_file = 'input/email_orig_html_doc.html'
    #laundered_fname = 'output/laundered.html'
    email_input_file = 'input/email_ex_01_step1.eml'
    HCOMEmailParser.parse_email(email_input_file)
    