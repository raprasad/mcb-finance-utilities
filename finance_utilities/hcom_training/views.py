from django.template import RequestContext
from django.shortcuts import render_to_response

from finance_utilities.common.msg_util import *

from django.template.loader import render_to_string
from django.core import serializers

from finance_utilities.hcom_training.models import Trainee, TraineeMessage


def view_hcom_confirmation(request, trainee_id):
    """Simple view showing trainee confirmation page"""
    lu = {}
    # Find the trainee; make sure he/she exists
    try:
        trainee = Trainee.objects.get(id_md5=trainee_id)
        lu.update({ 'trainee' : trainee })
    except Trainee.DoesNotExist:
        lu.update({ 'ERR_MSG' : True \
                , 'ERR_trainee_not_found' : True })
        return render_to_response('hcom_templates/hcom_confirm_page.html', lu, context_instance=RequestContext(request))
    
    # Check if the person has already confirmed      
    if trainee.confirmed_training_date:     # Yes, err message
        lu.update({ 'ERR_MSG' : True \
                , 'ERR_already_confirmed' : True })
    else:
        # New confirmation, update database
        trainee.confirmed_training_date = True
        trainee.save()
    
    # show confirmation page to use
    return render_to_response('hcom_templates/hcom_confirm_page.html', lu, context_instance=RequestContext(request))
    

def view_hcom_trainee_email_addresses(request):
    if not (request.user.is_authenticated() and request.user.is_staff):  
        return HttpResponse('not accessible')

    lu = {}

    if request.method == 'GET':  
        kwargs = {}
        for x,y in request.GET.iteritems():
            if not str(x) in ['ot', 'o', 'q']:
                kwargs.update({str(x):str(y)})
        #print kwargs
        try:
            trainees = Trainee.objects.filter(**kwargs).order_by('lname','fname')
        except:
            trainees = Trainee.objects.all().order_by('lname','fname')    
    else:
        trainees = Trainee.objects.all().order_by('lname','fname')

    if trainees.count() == 0:
        lu.update({'ERR_no_trainees' : True})
    else:
        lu.update({'trainees' : trainees})

    return render_to_response('hcom_templates/hcom_view_email_addresses.html', lu, context_instance=RequestContext(request))
    




