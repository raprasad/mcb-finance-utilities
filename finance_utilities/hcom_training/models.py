from django.db import models
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField

from django.core.urlresolvers import reverse
import hashlib 

class Special(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Designations (Faculty, staff, PD, etc)'
        verbose_name_plural = verbose_name
        
class LabOffice(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
  
class LocationInfo(models.Model):
    name = models.CharField(max_length=255)
    training_type = models.CharField(max_length=100)
    training_date = models.DateField()
    training_time = models.TimeField()
    week_num = models.CharField(max_length=20)
    room = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('training_date', 'name',)
        verbose_name = 'Location Information'
        verbose_name_plural = verbose_name 

TYPE_APPROVER = 'APPROVER'
TYPE_SHOPPER = 'SHOPPER'
class Trainee(models.Model):
    fname = models.CharField('first name', max_length=50)
    lname = models.CharField('last name', max_length=50)
    
    active = models.BooleanField(default=True, help_text='Uses or plans to use the HCOM system')
    special = models.ForeignKey(Special)#, blank=True, null=True)
    email = models.EmailField(blank=True)
    
    hands_on_training_date = models.DateField(blank=True, null=True)
    has_hands_on_training = models.BooleanField(default=False, help_text='auto-filled')

    demo_training_date = models.DateField(blank=True, null=True)
    has_demo_training = models.BooleanField(default=False, help_text='auto-filled')

    confirmed_training_date = models.BooleanField(default=False)
    completed_training = models.BooleanField(default=False)
    
    location = models.ForeignKey(LocationInfo, blank=True, null=True, help_text='auto-filled based on training date')
    
    approver_or_shopper = models.CharField(max_length=25, choices=((TYPE_APPROVER, 'approver'), (TYPE_SHOPPER, 'shopper')) )
    
    lab_or_office = models.ForeignKey(LabOffice)
    
    training_order = models.IntegerField(default=99)
    
    notes = models.TextField(blank=True)
    
    last_update = models.DateTimeField(auto_now=True)
    
    id_md5 = models.CharField(max_length=32, blank=True, help_text='Auto-fill on save')   

    
    def save(self,  *args, **kwargs):
        if not self.id_md5:
            super(Trainee, self).save( *args, **kwargs)      # save to have an 'id'
            #self.id_md5 =  md5.new(str(self.id)).hexdigest()
            self.id_hash =  hashlib.sha1('%s%s%s' % (self.id, self.lname, self.email)).hexdigest()
        self.update_location()
                
        
        if self.hands_on_training_date:
            self.has_hands_on_training = True
        else:
            self.has_hands_on_training = False

        if self.demo_training_date:
            self.has_demo_training = True
        else:
            self.has_demo_training = False

        super(Trainee, self).save( *args, **kwargs)      # save to have an 'id'
    
    
    def num_emails_sent(self):
        return TraineeMessage.objects.filter(trainee=self).count()
    
    def confirmation_link(self):
        if self.id:
            return reverse('view_hcom_confirmation', kwargs={ 'trainee_id' : self.id_md5 })
        return ''
    confirmation_link.allow_tags = True
    
    def update_location(self):
        if self.hands_on_training_date:
            locations = LocationInfo.objects.filter(training_date=self.hands_on_training_date)
            if locations.count() > 0:
                self.location = locations[0]    
                return
                
        if self.demo_training_date:
            locations = LocationInfo.objects.filter(training_date=self.demo_training_date)
            if locations.count() > 0:
                self.location = locations[0]    
                return

                
                
    def __unicode__(self):
        return '%s, %s'% (self.lname, self.fname)

    class Meta:
        ordering = ( 'lname', 'fname',)  


class TraineeMessage(models.Model):
    trainee = models.ForeignKey(Trainee)
    time_sent = models.DateTimeField(auto_now_add=True)
    to_address = models.CharField(max_length=200)
    msg = models.TextField()
    
    def __unicode__(self):
        return '%s - %s' % (self.trainee, self.time_sent)
    
    class Meta:
        ordering = ('trainee', '-time_sent',)  
    
'''
from mcb.hu_ldap.models import HarvardPersonInfo
l = HarvardPersonInfo.objects.all()
for p in l: p.save()

'''