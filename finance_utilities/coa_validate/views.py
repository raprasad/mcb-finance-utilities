from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.conf import settings 
from finance_utilities.coa_validate.expense_code_validator import ExpenseCodeValidator, SUBSTITUTE_OBJECT_CODE

from finance_utilities.coa_validate.forms import ExpenseCodeValidationForm, MAX_EXPENSE_CODES_TO_VALIDATE
from finance_utilities.coa_validate.forms_define import ExpenseCodeLookupForm

from coa_validate.models import CheckedExpenseCode, COADefinitionLoadLog

from expense_code_definitions.ec_lookup import ExpenseCodeDefined, NOT_FOUND
from expense_code_definitions.models import RootValue

from django.template.loader import render_to_string
from django.core import serializers


COOKIE_ATTR_SAVED_EC_CODES  = 'saved_ec_codes'

def get_coa_log_date():
    try:
        return COADefinitionLoadLog.objects.all()[0]
    except:
        return None

def get_previously_checked_expense_codes(request):
    for k, v in  request.session.items():
        print k, v
    ec_code_list = request.session.get(COOKIE_ATTR_SAVED_EC_CODES, [])
    #print 'ec_code_list', ec_code_list
    if len(ec_code_list) is None:
        return None
    #print CheckedExpenseCode.objects.filter(id__in=ec_code_list)
    
    return CheckedExpenseCode.objects.filter(id__in=ec_code_list)
    
def update_checked_expense_codes(request, ec_validation_results):
    """Update saved codes in the cookies"""
    #print 'request', request
    if request is None or not ec_validation_results:
        return 

    ec_validation_results = filter(lambda x: x.checked_expense_code, ec_validation_results)
    checked_ec_code_ids = map(lambda x: x.checked_expense_code.id, ec_validation_results)
    if len(checked_ec_code_ids) == 0:
        return
        
    updated_code_list = request.session.get(COOKIE_ATTR_SAVED_EC_CODES, [])
    for ec_code in checked_ec_code_ids:
        if not ec_code in updated_code_list:
            updated_code_list.append(ec_code)
    request.session[COOKIE_ATTR_SAVED_EC_CODES] = updated_code_list


def view_ec_validation_form(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        COOKIES_ON = True
        print 'yes cookies'
    else:
        COOKIES_ON = False
        print 'no cookies'
        
    lu = { 'VALIDATE_PAGE' : True\
        , 'NOT_FOUND' : NOT_FOUND\
        , 'SUBSTITUTE_OBJECT_CODE' : SUBSTITUTE_OBJECT_CODE\
        , 'MAX_EXPENSE_CODES_TO_VALIDATE' : MAX_EXPENSE_CODES_TO_VALIDATE\
        , 'COOKIES_ON' : COOKIES_ON
        , 'coa_load_log' : get_coa_log_date()
         }

    if request.method=='POST':        
        ec_form = ExpenseCodeValidationForm(request.POST)
        if ec_form.is_valid():
            print 'valid!'
            ec_validation_results = ec_form.get_code_validation_results()
            update_checked_expense_codes(request, ec_validation_results.validation_response_objects)
            ec_form = ExpenseCodeValidationForm()
            lu.update( { 'validation_results' : ec_validation_results })
            #return render_to_response('ec_validate/view_ec_validation_form.html', lu, context_instance=RequestContext(request))
        else:
            print 'NOT valid!'
            lu.update({ 'ERR_form_not_valid' : True })
    else: 
        ec_form = ExpenseCodeValidationForm()#**kw={ 'resources' : resources})

    lu.update({ 'ec_form' : ec_form\
            ,   'my_checked_codes' : get_previously_checked_expense_codes(request)\
            })

    return render_to_response('ec_validate/ec_validation.html', lu, context_instance=RequestContext(request))

def view_mcb_roots(request):
    lu = { 'MCB_ROOTS_PAGE' : True\
            , 'mcb_roots' : RootValue.objects.filter(desc__contains='MCB', enabled_flag=True).order_by('desc')
            , 'my_checked_codes' : get_previously_checked_expense_codes(request)\
            , 'coa_load_log' : get_coa_log_date()
            
         }

    return render_to_response('ec_validate/mcb_roots.html', lu, context_instance=RequestContext(request))
    
    

def view_define_ec_form(request):

    lu = { 'DEFINE_PAGE' : True\
        , 'NOT_FOUND' : NOT_FOUND\
        , 'SUBSTITUTE_OBJECT_CODE' : SUBSTITUTE_OBJECT_CODE\
        , 'MAX_EXPENSE_CODES_TO_VALIDATE' : MAX_EXPENSE_CODES_TO_VALIDATE\
        , 'coa_load_log' : get_coa_log_date()
         }

    if request.method=='POST':        
        ec_form = ExpenseCodeLookupForm(request.POST)
        if ec_form.is_valid():
            expense_code_defined = ec_form.get_definitions()
            lu.update( { 'ec_description_dict' : expense_code_defined.get_ec_description_dict()})

            exp_code_str = expense_code_defined.get_ec_str()
            if exp_code_str is not None:
                validate_response =  ExpenseCodeValidator(use_test_server=settings.DEBUG).validate_expense_code(exp_code_str)
                update_checked_expense_codes(request, [validate_response])
                
                lu.update( { 'validate_response' : validate_response })
                
        else:
            print 'NOT valid!'
            lu.update({ 'ERR_form_not_valid' : True })
    else: 
        ec_form = ExpenseCodeLookupForm()#**kw={ 'resources' : resources})
    
    lu.update({ 'ec_form' : ec_form\
        ,   'my_checked_codes' : get_previously_checked_expense_codes(request)\
     })

    return render_to_response('ec_validate/ec_define.html', lu, context_instance=RequestContext(request))

def view_my_codes(request):
    
    my_checked_codes =  get_previously_checked_expense_codes(request)
    
    fmt_list = []
    if my_checked_codes is not None:
        for mc in my_checked_codes:
            mc.define_ec()
            fmt_list.append(mc)
        num_codes = len(fmt_list)
    else:
        num_codes = 0
    
    lu = { 'MY_CHECKED_CODES_PAGE' : True\
        ,   'my_checked_codes' : fmt_list\
        , 'num_codes' : num_codes
        , 'coa_load_log' : get_coa_log_date()
     }

    return render_to_response('ec_validate/my_codes.html', lu, context_instance=RequestContext(request))
   
