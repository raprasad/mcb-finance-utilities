from django.db import models
from django.core.urlresolvers import reverse
from hcom_reconcile.models import RequisitionEmail, HcomPersonName, HcomUnit
from django.db.models.signals import pre_save, post_save, post_delete   

    
class PurchaseOrderEmail(models.Model):
    hcom_idnum = models.IntegerField(db_index=True, unique=True, help_text='unique to the email')
    purchase_order_num = models.CharField(max_length=50, unique=True, db_index=True, help_text='from the email subject line')
    requisition_email = models.ForeignKey(RequisitionEmail, unique=True, blank=True, null=True, on_delete=models.PROTECT)
    
    is_matched = models.BooleanField(default=False)
    
    from_name = models.ForeignKey(HcomPersonName, related_name='po_from_name', on_delete=models.PROTECT)
    to_name = models.ForeignKey(HcomPersonName, related_name='po_to_name', on_delete=models.PROTECT)
    
    sent_time = models.DateTimeField()
    
    notes = models.TextField(blank=True)
    email_html = models.TextField(blank=True)
    
    total_amt = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amt = models.DecimalField(max_digits=12, decimal_places=2)
    
    last_update = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        if self.requisition_email:
            self.is_matched = True
        else:
            self.is_matched = False
        
        super(PurchaseOrderEmail, self).save(*args, **kwargs)
    
    def line_item_count(self):
        return self.get_line_item_count()
    
    def get_line_item_descriptions(self):
        dlist = []
        for li in self.purchaseorderlineitem_set.filter(purchase_order=self):
            if not li.description in dlist:
                dlist.append(li.description)
        dlist.sort()
        return dlist
    
    def get_line_item_count(self):
        return self.purchaseorderlineitem_set.filter(purchase_order=self).count()
    
    def req_link(self):
        if self.requisition_email:
            req_lnk = reverse('admin:hcom_reconcile_requisitionemail_change'\
                                , args=(self.requisition_email.id,))
            return '<a href="%s">View Requisition</a>' % (req_lnk)
        return 'n/a'
    req_link.allow_tags = True
    
    def __unicode__(self):
        if self.requisition_email:
            return 'PO: %s [Req: %s]'  % \
                    (self.purchase_order_num, self.requisition_email.requisition_num)        
        return 'PO: %s' % self.purchase_order_num

    class Meta:
        ordering = ('-hcom_idnum', 'purchase_order_num')
        verbose_name = ('Email 2: Purchase order email')



class PurchaseOrderLineItem(models.Model):

    purchase_order = models.ForeignKey(PurchaseOrderEmail, on_delete=models.PROTECT)
    line_num = models.IntegerField()

    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    unit = models.ForeignKey(HcomUnit, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    item_number = models.CharField(max_length=255, blank=True)
    rev = models.CharField(max_length=50, blank=True)
    
    last_update = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return 'Req #%s, Line %s, %s' % (self.purchase_order.purchase_order_num, self.line_num, self.description)

    class Meta:
        ordering = ('purchase_order', 'line_num',)
        verbose_name = ('Email 2a: Purchase order line item')

post_delete.connect(RequisitionEmail.update_po_match, sender=PurchaseOrderEmail)
post_save.connect(RequisitionEmail.update_po_match, sender=PurchaseOrderEmail)
