"""
Working on the hu ldap / personnel db connection
"""
if __name__=='__main__':
    #-------------------------
    # import django settings
    #-------------------------
    import os, sys
    #sys.path.append('../../mcb')
    from django.core.management import setup_environ
    import settings
    setup_environ(settings)

from finance_utilities.common.msg_util import *
from finance_utilities.hcom_training.models import *

import datetime
from django.template.loader import render_to_string

#from mcb.common.mailer import send_message
from django.core.mail import EmailMessage, EmailMultiAlternatives


def send_hcom_training_email(trainee, really_send=False):
    if trainee is None:
        print 'not trainee'; return False;
    if trainee.email in ['', None]:
        print 'no email'; return False;
    if trainee.location is None:
        print 'no location'; return False;
        
    print '> prepare email'
    lu = { 'trainee' : trainee }

    #msg_html = render_to_string('hcom_templates/email/confirmation_email.html', lu)
    if trainee.special and trainee.special.name.lower().strip() == 'faculty':
        msg_text = render_to_string('hcom_templates/email/confirmation_email_faculty.txt', lu)
    elif trainee.approver_or_shopper == TYPE_APPROVER:
        msg_text = render_to_string('hcom_templates/email/confirmation_email_approver.txt', lu)
    elif trainee.approver_or_shopper == TYPE_SHOPPER:
        msg_text = render_to_string('hcom_templates/email/confirmation_email_shopper.txt', lu) 
    else:
        msgx('send_hcom_training_email: unknown email template for (%s)' % trainee)
    
    #subject = 'HCOM LOCATION CORRECTION: %s' % trainee.location.name
    subject = 'Save the date - REQUIRED MCB HCOM %s' % trainee.location.name
     
    
    #from_email ='Jessica Manning <jmanning@mcb.harvard.edu>'
    if really_send:
        from_email ='Jessica Manning <jmanning@mcb.harvard.edu>'
        to_addresses = [trainee.email] #[signup.email]
        bcc = ('some-admin@harvard.edu', )
    else:
        from_email ='user name <some-admin@harvard.edu>'
        to_addresses = [from_email] #[signup.email]
        bcc = ('some-admin@harvard.edu', )
        
   
    email = EmailMessage(subject, msg_text, from_email,
                   to_addresses, 
                   bcc,
                   headers = {'Reply-To': 'jmanning@mcb.harvard.edu'})
    
    if 1:
        email.send(fail_silently=False)
        print 'trainee', trainee
        print 'subject', subject
        print 'to_addresses', to_addresses
        tm = TraineeMessage(trainee=trainee \
                    , time_sent=datetime.datetime.now()\
                    , to_address=str(to_addresses) \
                    , msg='subject: %s\n\n%s' % (subject, msg_text)
                    )
        tm.save()
        return True
    #except:
    #    return False


def send_rsvp_emails(really_send=False):
    cnt =0
    loc = LocationInfo.objects.get(pk=8)
    for trainee in Trainee.objects.filter(location=loc):
        cnt +=1
        print ''
        dashes()
        print '(%s) trainee: %s' %  (cnt, trainee)
        if TraineeMessage.objects.filter(trainee=trainee).count() > 0:
            print 'msg already sent'
        else:
            if send_hcom_training_email(trainee, really_send):
                print 'MSG Sent!'
            else:
                print 'ERR >> Failed to send message'

        #if cnt==1: break
if __name__=='__main__':
    sys.exit(0)
    if len(sys.argv)==2:

        #for tid in (1216, 1233, 1225, 1335, 1311, 1394, 1397, 1419):
        print 'email for trainee', sys.argv[1]
        try:
            #trainee = Trainee.objects.get(pk=tid)
            trainee = Trainee.objects.get(pk=sys.argv[1])
        except Trainee.DoesNotExist:
            msgx('trainee with id %s not found' % sys.argv[1])
        send_hcom_training_email( trainee, really_send=True)
            
        
    else:
        send_rsvp_emails(really_send=False)


