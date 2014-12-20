from django.db import models
from django.core.urlresolvers import reverse
import hashlib 

class HcomPersonName(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __unicode__(self):
        return self.name
        
    @staticmethod
    def get_hcom_person_name(name_val):
        if name_val is None: return None
        name_val = name_val.strip()
        if len(name_val) == 0: return None
        try:
            return HcomPersonName.objects.get(name=name_val)
        except HcomPersonName.DoesNotExist:
            h = HcomPersonName(name=name_val)
            h.save()
            return h
            
    class Meta:
        ordering = ('name', )
        verbose_name = 'HCOM person name'     
        

class HcomCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __unicode__(self):
        return self.name

    @staticmethod
    def get_hcom_category(val):
        if val is None: return None
        val = val.strip()
        if len(val) == 0: return None
        try:
            return HcomCategory.objects.get(name=val)
        except HcomCategory.DoesNotExist:
            h = HcomCategory(name=val)
            h.save()
            return h
            
    class Meta:
        ordering = ('name', )   
        verbose_name = 'HCOM category'     
        verbose_name_plural = 'HCOM categories'     

class HcomSupplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __unicode__(self):
        return self.name
    
    @staticmethod
    def get_hcom_supplier(val):
        if val is None: return None
        val = val.strip()
        if len(val) == 0: return None
        try:
            return HcomSupplier.objects.get(name=val)
        except HcomSupplier.DoesNotExist:
            h = HcomSupplier(name=val)
            h.save()
            return h

    class Meta:
        ordering = ('name', ) 
        verbose_name = 'HCOM supplier'     

class HcomSite(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __unicode__(self):
        return self.name
    
    @staticmethod
    def get_hcom_site(val):
        print 'get_hcom_site: [%s]' % val
        if val is None: return None
        val = val.strip()
        if len(val) == 0: return None
        try:
            return HcomSite.objects.get(name=val)
        except HcomSite.DoesNotExist:
            h = HcomSite(name=val)
            h.save()
            return h
            
    class Meta:
        ordering = ('name', )               
        verbose_name = 'HCOM site'     

class HcomUnit(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __unicode__(self):
        return self.name
  
    @staticmethod
    def get_hcom_unit(val):
        if val is None: return None
        val = val.strip()
        if len(val) == 0: return None
        try:
            return HcomUnit.objects.get(name=val)
        except HcomUnit.DoesNotExist:
            h = HcomUnit(name=val)
            h.save()
            return h
            
    class Meta:
        ordering = ('name', )               
        verbose_name = 'HCOM unit'     


class RequisitionEmail(models.Model):
    """Information from HCOM Email 1"""
    hcom_idnum = models.IntegerField(db_index=True, unique=True, help_text='unique to the email')
    requisition_num = models.CharField(max_length=50, db_index=True, unique=True, help_text='from the email subject line')
    purchase_order_num = models.CharField(max_length=50, db_index=True, blank=True, help_text='Auto-filled if records match')
    
    from_name = models.ForeignKey(HcomPersonName, related_name='from_name')
    to_name = models.ForeignKey(HcomPersonName, related_name='to_name')
    
    is_matched = models.BooleanField(default=False)
    
    sent_time = models.DateTimeField()
    description = models.CharField(max_length=255)
    
    requisition_total = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_tax = models.DecimalField(max_digits=12, decimal_places=2)
    
    notes = models.TextField(blank=True)
    email_html = models.TextField(blank=True)
    
    last_update = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    @staticmethod
    def update_po_match(sender, is_post_delete=False, **kwargs):
        """As AlumnusPosition objects are added/deleted; Update the attribute "has_current_position" """

        purchase_order_email = kwargs.get('instance', None)
        if purchase_order_email is None:
            return

        try:
            if purchase_order_email.requisition_email is not None:
                requisition_email_obj = purchase_order_email.requisition_email
                requisition_email_obj.save()
        except:
            pass
        
        # check for missing POs
        # Not often: PO changes related Req. to another object
        reqs = RequisitionEmail.objects.filter(is_matched=True)
        reqs = filter(lambda x: x.get_related_purchase_order() is None, reqs)
        for r in reqs:
            r.save()    # update is_matched
        
        
    def get_line_item_count(self):
        return self.requisitionlineitem_set.filter(requisition=self).count()
    
    def get_line_item_descriptions(self):
         dlist = []
         for li in self.requisitionlineitem_set.filter(requisition=self):
             if not li.description in dlist:
                 dlist.append(li.description)
         dlist.sort()
         return dlist
             
    def get_calculated_line_item_count(self):
        """
        Only count each item description a single time.
        e.g., the same item, purchased with 2 different expense codes, is counted once
        """
        keyed_cnts = {}
        for li in self.requisitionlineitem_set.filter(requisition=self):
            keyed_cnts[li.description]  = 1
        #print 'sum', sum(keyed_cnts.values())
        return sum(keyed_cnts.values())
        
    def get_related_purchase_order(self):
        try:
            return self.purchaseorderemail_set.get(requisition_email=self)
        except:
            return None

    
    def save(self, *args, **kwargs):
        related_po = self.get_related_purchase_order()
        if related_po is not None:
            self.is_matched = True
            self.purchase_order_num = related_po.purchase_order_num
        else:
            self.is_matched = False
            self.purchase_order_num = ''
        
        super(RequisitionEmail, self).save(*args, **kwargs)
    
    def line_item_count(self):
        return self.get_line_item_count()
        
    def view_po(self):
        po_obj = self.get_related_purchase_order()
        if po_obj is None:
            return 'n/a'
            
        po_lnk = reverse('admin:hcom_reconcile_purchaseorderemail_change'\
                                , args=(po_obj.id,))
        return '<a href="%s">View PO</a>' % (po_lnk)
    view_po.allow_tags = True
    
    
    def __unicode__(self):
        return 'Requisition %s' % self.requisition_num
        
    class Meta:
        ordering = ('-hcom_idnum', 'requisition_num',)
        verbose_name = ('Email 1: Requisition Email')
        

class RequisitionLineItem(models.Model):
    
    requisition = models.ForeignKey(RequisitionEmail, on_delete=models.PROTECT)
    line_num = models.IntegerField()
    description = models.TextField()
    category = models.ForeignKey(HcomCategory, on_delete=models.PROTECT)
    supplier = models.ForeignKey(HcomSupplier, on_delete=models.PROTECT)
    site = models.ForeignKey(HcomSite, on_delete=models.PROTECT)
    charge_account = models.CharField('Billing Code', max_length=255)
    charge_root = models.CharField(max_length=10, blank=True, help_text='populated from charge account')
    unit = models.ForeignKey(HcomUnit)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    last_update = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def purchase_order_num(self):
        if self.requisition and self.requisition.purchase_order_num:
            return self.requisition.purchase_order_num
        return 'n/a'
    purchase_order_num.allow_tags = True

    def save(self,  *args, **kwargs):
        if self.charge_account:
            self.charge_root = self.charge_account[-5:]
        super(RequisitionLineItem, self).save( *args, **kwargs)      # save to have an 'id'
        
    def __unicode__(self):
        return 'Req #%s, Line %s, %s' % (self.requisition.requisition_num, self.line_num, self.description)
    
    class Meta:
        ordering = ('requisition', 'line_num',)
        verbose_name = ('Email 1a: Requisition line item')
    
from hcom_reconcile.models_purchase_order import *