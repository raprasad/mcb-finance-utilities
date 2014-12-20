from finance_utilities.hcom_training.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class SpecialAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
admin.site.register(Special, SpecialAdmin)

class LabOfficeAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',)
admin.site.register(LabOffice, LabOfficeAdmin)


class TraineeMessageInline(admin.TabularInline):
    model = TraineeMessage
    readonly_fields= ['time_sent', ]
    extra=0

class TraineeMessageAdmin(admin.ModelAdmin):
    save_on_top = True
    readonly_fields= ['time_sent', ]
    list_display = ('trainee', 'time_sent', 'msg',)
    extra=0
admin.site.register(TraineeMessage, TraineeMessageAdmin)

class LocationInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'training_date', 'training_time', 'week_num', 'room',)

admin.site.register(LocationInfo, LocationInfoAdmin)


class TraineeAdmin(admin.ModelAdmin):
    
    save_on_top = True
    inlines = [ TraineeMessageInline, ]
    
                        
    list_display = ('lname','fname',   'email', 'active', 'completed_training',  'special', 'approver_or_shopper', 'lab_or_office', )
    list_editable = ('completed_training',  )
    
    search_fields = ('lname', 'fname', 'email',)
    list_filter = ('active', 'confirmed_training_date', 'completed_training','has_hands_on_training', 'has_demo_training','special','approver_or_shopper', 'location',)
    
    readonly_fields = ( 'has_hands_on_training', 'has_demo_training', 'last_update', 'id_md5', 'num_emails_sent','confirmation_link' )
    
    fieldsets = [
            ('name / email',  {'fields': [( 'fname','lname',), 'active', 'email', 'special', 'lab_or_office','last_update', 'num_emails_sent',]})
            
            ,('training', {'fields': ['confirmed_training_date', 'completed_training', 'training_order', 'approver_or_shopper', 'location', ('has_hands_on_training', 'hands_on_training_date',)\
                ,  ('has_demo_training',  'demo_training_date'),  ]})\
            ,('Notes', {'fields': [ 'notes', 'id_md5' ,'confirmation_link' ]})\
      ]

admin.site.register(Trainee, TraineeAdmin)

#admin.site.register(LocationInfo)

#class TraineeAdmin(admin.ModelAdmin):
#    list_display = ('lname','fname',   'email', 'confirmed_training_date','completed_training')
#    #search_fields = ('lname', 'fname', 'email', 'location__room')
#    #list_filter = ('confirmed_training_date', 'completed_training', 'location')
#admin.site.register(Trainee, TraineeAdmin)

