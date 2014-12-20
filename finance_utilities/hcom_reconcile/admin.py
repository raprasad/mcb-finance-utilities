from finance_utilities.hcom_reconcile.models import *
from finance_utilities.hcom_reconcile.forms import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class HcomNameAttrAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)


admin.site.register(HcomPersonName, HcomNameAttrAdmin)
admin.site.register(HcomCategory, HcomNameAttrAdmin)
admin.site.register(HcomSupplier, HcomNameAttrAdmin)
admin.site.register(HcomSite, HcomNameAttrAdmin)
admin.site.register(HcomUnit, HcomNameAttrAdmin)


class RequisitionLineItemInline(admin.TabularInline):
    model = RequisitionLineItem
    form = RequisitionLineItemInlineForm
    readonly_fields= ['charge_root', 'purchase_order_num',]
    extra=0

class RequisitionLineItemAdmin(admin.ModelAdmin):
    form = RequisitionLineItemAdminForm
    save_on_top = True
    list_display = ('requisition', 'purchase_order_num', 'line_num',  'charge_root', 'description', 'amount', 'charge_account', 'category', 'supplier',  'site', 'unit',  'quantity', 'price' )
    #list_editable = ('completed_training',  )
    readonly_fields = ( 'date_added', 'last_update', 'purchase_order_num')
    search_fields = ('description', 'charge_root', 'description', 'charge_account','requisition__requisition_num',)
    list_filter = ('charge_root',)
    
    fieldsets = [
          ('Basic',  {'fields': [ 'requisition','line_num', 'description', \
            ('charge_account', 'charge_root',), 'unit'\
                , ('price', 'quantity', 'amount', )\
                ]})
            ,('Category / Supplier / Site', {'fields': [ 'category', 'supplier',  'site', ]})\

            ,('Time stamps', {'fields': [ ('last_update', 'date_added' ,), ]})\
    ]
admin.site.register(RequisitionLineItem, RequisitionLineItemAdmin)

class RequisitionEmailAdmin(admin.ModelAdmin):
    form = RequisitionEmailAdminForm
    save_on_top = True
    inlines = [ RequisitionLineItemInline, ]
    list_display = ('requisition_num', 'purchase_order_num', 'hcom_idnum',  'is_matched',  'view_po', 'requisition_total', 'line_item_count', 'from_name', 'to_name', 'sent_time',  'description','estimated_tax', )
    #list_editable = ('completed_training',  )
    
    search_fields = ('from_name__name', 'to_name__name', 'description', 'hcom_idnum','requisition_num', 'requisition_total')
    list_filter = ( 'is_matched', 'from_name', 'from_name', )
    
    readonly_fields = ( 'email_html', 'last_update', 'date_added', 'view_po', 'line_item_count', 'is_matched' )

    fieldsets = [
          ('Basic',  {'fields': [( 'requisition_num','hcom_idnum',), 
            ('is_matched','view_po',), 'line_item_count', 'description',  \
            ('from_name', 'to_name',), 'sent_time', ('requisition_total', 'estimated_tax',)]})
            ,('Time stamps', {'fields': [ ('last_update', 'date_added' ,), ]})\
          
          ,('Notes', {'fields': ['notes',  ]})\
          ,('Original HTML', {  'classes': ('collapse',)\
            ,'fields': ['email_html',  ]})\
    ]
admin.site.register(RequisitionEmail, RequisitionEmailAdmin)

class PurchaseOrderLineItemInline(admin.TabularInline):
    model = PurchaseOrderLineItem
    form = PurchaseOrderLineItemInlineForm
    readonly_fields= [ 'last_update', 'date_added' ]
    extra=0


class PurchaseOrderEmailAdmin(admin.ModelAdmin):
    form = PurchaseOrderAdminForm
    save_on_top = True
    inlines = [ PurchaseOrderLineItemInline, ]
    list_display = ('purchase_order_num', 'hcom_idnum',  'is_matched', 
    'requisition_email',  'req_link', 'line_item_count',   'total_amt', 'tax_amt', 'from_name', 'to_name', 'sent_time',)
    #list_editable = ('completed_training',  )
    
    search_fields = ('from_name__name', 'to_name__name', 'hcom_idnum', 'purchase_order_num','requisition_email__requisition_num','total_amt',)
    list_filter = ('is_matched', 'from_name', 'from_name', )
    
    readonly_fields = ( 'email_html', 'last_update', 'date_added','req_link', 'line_item_count', 'is_matched')

    fieldsets = [
          ('Basic',  {'fields': [( 'purchase_order_num','hcom_idnum',)\
                    , ('is_matched', 'requisition_email',  'req_link',), 'line_item_count'\
            , ('from_name', 'to_name',), ('total_amt', 'tax_amt',), 'sent_time']})\
            ,('Time stamps', {'fields': [ ('last_update', 'date_added',), ]})\
          
          ,('Notes', {'fields': ['notes',  ]})\
          ,('Original HTML', {  'classes': ('collapse',), 'fields': ['email_html',  ]})\
    ]
admin.site.register(PurchaseOrderEmail, PurchaseOrderEmailAdmin)
  
  
class PurchaseOrderLineItemAdmin(admin.ModelAdmin):
    #form = RequisitionLineItemAdminForm
    save_on_top = True
    list_display = ('purchase_order',  'line_num',  'description', 'amount', 'unit',  'quantity', 'price' , 'item_number', 'rev')
    #list_editable = ('completed_training',  )
    readonly_fields = ( 'date_added', 'last_update', )
    search_fields = ('description', 'purchase_order__purchase_order_num',)
    
    fieldsets = [
          ('Basic',  {'fields': [ 'purchase_order','line_num', 'description', 'unit'\
                , ('price', 'quantity', 'amount', )\
                ]})
            ,('Item Number / Rev', {'fields': [ 'item_number', 'rev',]})\

            ,('Time stamps', {'fields': [ ('last_update', 'date_added' ,), ]})\
    ]
admin.site.register(PurchaseOrderLineItem, PurchaseOrderLineItemAdmin)