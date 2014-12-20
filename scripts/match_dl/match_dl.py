import xlrd
import re
from decimal import Decimal

PO_CATEGORY = 'Purchase Invoices'
FREIGHT_ORDER = 'freight'
class DetailedListing:
    col_names = ['journal_category', 'batch_name', 'journal_header', 'transaction_line_description', 'fund_distribution', 'object_code', 'description', 'id_reference_number', 'amount', 'date', 'reconciled', 'year_logic', 'type', 'fund_subact', 'fund_title', 'fund_status', 'tub', 'org', 'fund', 'activity', 'subactivity', 'root', 'object_category', 'object_description', 'adi_journal_line_description', 'adi_journal_dff_description']
    date_attrs = ['date']
    
    def __init__(self, xls_row):
        if xls_row is None:
             raise Exception('xls_row is None')
        
        self.po_order_number = None
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
           
        if self.journal_category==PO_CATEGORY and not self.is_freight_order():
            self.is_po_order = True
            self.pull_purchase_order()
        
        print 'row loaded'
    
    
    
    def is_freight_order(self):
        if self.transaction_line_description is None:
            return False
            
        if self.transaction_line_description.lower() == FREIGHT_ORDER:
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
        
        print '# detail listings', len(self.detail_listings)
        
        po_listings = filter(lambda x: x.is_po_order, self.detail_listings )
        print '# PO listings', len(po_listings)
        
        for po in po_listings:
            print po.po_order_number
        
                
            
if __name__=='__main__':    
    fname = "user-PO TEST 's PI's DOWNLOAD APRIL2013.xlsx"
    dlr = DLReader(fname)
    