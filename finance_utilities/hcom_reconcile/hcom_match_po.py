"""
Attempt to match a Requisition Record to a PO

- Criteria (evolving)
    - timestamp match, within 20 seconds
    - hcom_idnum, within 10 numbers
    - descriptions of line items
"""
from hcom_reconcile.models import RequisitionEmail, RequisitionLineItem, PurchaseOrderEmail, PurchaseOrderLineItem
from common.msg_util import *
from datetime import datetime, timedelta
 
class RecordMatcher:
    """
    Requisition email sent, soon followed by a PurchaseOrder Email
    
    - match the PurchaseOrder Email to the Requisition email
    """
    def __init__(self, po_record):
        self.po_record = po_record
        self.requisition_sent_seconds_range = -30
        self.find_match()
        
    def find_match(self):
        """
        Current match criteria:

            (1) Sent time
                - Req email sent earlier than PO email -- within 30 seconds
            (2) HCOM ID
                - PO HCOM ID greater than Req HCOM ID, but number doesn't differ by more than 100
            (3) Total dollar amount - must be equal

            to do: (4) "To" address in the Req matches the "From" and "To" addresse in the PO

            (5a) Number of line items OR 
            to do: (5b) Number of calculated line items*
                * In the requisition: The same item, with the same charge code may appear in multiple line itmes, 
                In the PO: these line items are collapsed into a single item
            to do: (6) Line item descriptions?
            
        """
        #if self.po_record.requisition_email:
        #    print 'already matched'
        #    return
         
        req_email_min_time = self.po_record.sent_time + timedelta(seconds=self.requisition_sent_seconds_range)  
        
        po_rec_hcom_min_id =  self.po_record.hcom_idnum-100 
        print 'po_rec_hcom_min_id', po_rec_hcom_min_id
         

        req_filter_kwargs = { 'sent_time__lte' : self.po_record.sent_time\
                             , 'sent_time__gte' : req_email_min_time\
                             #, 'hcom_idnum' : hcom_rec_exact\
                             
                             , 'hcom_idnum__lt' : self.po_record.hcom_idnum\
                             , 'hcom_idnum__gt' : po_rec_hcom_min_id\
                             , 'requisition_total' : self.po_record.total_amt\
                             }
        
        dashes()
        print req_filter_kwargs
        dashes()
        
        potential_req_email_objs = RequisitionEmail.objects.filter(**req_filter_kwargs)
        
        # match "calculated" # of line items
        potential_req_email_objs = filter(lambda x: x.get_calculated_line_item_count() == self.po_record.get_line_item_count(), potential_req_email_objs)
        
        # match line item description 
        potential_req_email_objs = filter(lambda x: x.get_line_item_descriptions() == self.po_record.get_line_item_descriptions(), potential_req_email_objs)
    
        num_potential_matches = len(potential_req_email_objs)
        
        if num_potential_matches == 1:            
            req_email = potential_req_email_objs[0]
            self.po_record.requisition_email = req_email
            self.po_record.save()
            req_email.save()    # update match
            print 'Matched!'
        elif num_potential_matches > 1:
            print 'multiple matches possible'
        else:
            print 'no match'
       
