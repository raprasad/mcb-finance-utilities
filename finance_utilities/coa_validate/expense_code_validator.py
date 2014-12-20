"""
5/20/2012
Use the Office of Administrative Systems GL COA Validation Web-Based API
"""
import httplib
import re
import string
from urlparse import urlparse
from xml.dom import minidom  
from expense_code_definitions.ec_lookup import ExpenseCodeDefined, NOT_FOUND
from coa_validate.models import CheckedExpenseCode
import socket
import sys
from django.conf import settings


SUBSTITUTE_OBJECT_CODE = '6600'
SERVER_TIMEOUT_LIMIT = 2 # seconds

class ExpenseCodeValidationResults(object):
    def __init__(self, validation_response_objects):
        self.validation_response_objects = validation_response_objects
        self.num_responses = 0
        self.num_valid = 0
        self.num_server_fails = 0
        self.num_invalid = 0
        
        self.calc_stats()

    def calc_stats(self):
        if self.validation_response_objects is None:
            return 
        
        self.num_responses = len(self.validation_response_objects) 
        
        self.num_valid = len(filter(lambda x: x.is_valid, self.validation_response_objects))
        self.num_server_fails = len(filter(lambda x: x.is_server_connection_err, self.validation_response_objects))
        self.num_invalid = self.num_responses - (self.num_valid + self.num_server_fails)
            

class ValidationResponse(object):

    def __init__(self, orig_expense_code_str, expense_code_str, is_valid, msg='', is_server_connection_err=False):
        self.orig_expense_code_str = orig_expense_code_str
        self.expense_code_str = expense_code_str
        self.is_valid = is_valid
        self.msg = msg
        self.is_server_connection_err = is_server_connection_err
        self.ec_defined = None
        self.checked_expense_code = None
        
        self.define_ec()
        self.save_checked_expense_code()
        
    def define_ec(self):
        if not len(self.expense_code_str)==33:
            return
            
        self.ec_defined = ExpenseCodeDefined.load_ec_str(self.expense_code_str)
    
    def save_checked_expense_code(self):
        print 'save_checked_expense_code'
        if not len(self.expense_code_str)==33:
            return 
        print 'find existing: ', self.expense_code_str
        try:
            ec = CheckedExpenseCode.objects.get(expense_code=self.expense_code_str)
            ec.is_valid == self.is_valid   
            print 'find existing: ', self.expense_code_str
             
        except:
            ec = CheckedExpenseCode(expense_code=self.expense_code_str\
                                , is_valid=self.is_valid)

        ec.save()
        self.checked_expense_code = ec

    def get_fmt_ec_str(self):
        
        if not len(self.expense_code_str) == 33:
            return self.orig_expense_code_str
        elif self.expense_code_str is None or not len(self.expense_code_str) == 33:
            return self.orig_expense_code_str
        else:
            return '%s-%s-%s-%s-%s-%s-%s' % (self.expense_code_str[0:3]
                    , self.expense_code_str[3:8]
                    , self.expense_code_str[8:12]
                    , self.expense_code_str[12:18]
                    , self.expense_code_str[18:24]
                    , self.expense_code_str[24:28]
                    , self.expense_code_str[28:33]
                    )
                    
    def __str__(self):
        if self.is_valid:
            return 'VALID'
        else:
            return 'INVALID.  Error: %s' % self.msg
            

        
class ExpenseCodeValidator(object):
    STATUS_OK_200 = 200
    
    def __init__(self, use_test_server=True):
        if use_test_server:
            self.validator_url = settings.COA_VALIDATOR_URL_TEST
        else:
            self.validator_url = settings.COA_VALIDATOR_URL_PROD
            

    def validate_expense_code(self, expense_code_str):
        if expense_code_str is None:
            return ValidationResponse(None, None, is_valid=False, msg="Expense code string is None")
            
        ec_str_digits_only = re.sub("[^%sx]"% string.digits,"",expense_code_str)
        if not len(ec_str_digits_only) == 33:
            return ValidationResponse(expense_code_str, ec_str_digits_only, is_valid=False, msg="Expense code is not 33 digits.  Found %s digits." % len(ec_str_digits_only))

        if ec_str_digits_only[8:12] == 'xxxx':
            ec_str_digits_only = ec_str_digits_only.lower().replace('xxxx', SUBSTITUTE_OBJECT_CODE)
        if not ec_str_digits_only.isdigit():
            return ValidationResponse(expense_code_str, ec_str_digits_only, is_valid=False, msg="This expense code has non-digits.  This is only allowed for the : [%s]" % ec_str_digits_only)

        ec_xml = self.get_xml_request(ec_str_digits_only)
        #print ec_xml
        if ec_xml is None:
            return ValidationResponse(expense_code_str, ec_str_digits_only, is_valid=False, msg="This expense code is not 33 digits.  Found %s digits." % len(ec_str_digits_only))

        url_parts = urlparse(self.validator_url)
        # e.g. ParseResult(scheme='https', netloc='test-server-34:8852', path='/GLValidate/ValidateGLAccount', params='', query='', fragment='')
        

        headers = {"Content-type": "text/xml"}
        
        if url_parts.scheme == 'https':
            server_conn = httplib.HTTPSConnection(url_parts.netloc, timeout=SERVER_TIMEOUT_LIMIT)
        else:
            server_conn = httplib.HTTPConnection(url_parts.netloc, timeout=SERVER_TIMEOUT_LIMIT)
            

        try:
            server_conn.request('POST', url_parts.path, ec_xml, headers)
            response = server_conn.getresponse()
        except socket.timeout:
            return ValidationResponse(expense_code_str, ec_str_digits_only, is_valid=False, msg="Sorry!  The server was not available.  (request timed out after %s seconds)" % SERVER_TIMEOUT_LIMIT, is_server_connection_err=True)
        except:
            return ValidationResponse(expense_code_str, ec_str_digits_only, is_valid=False, msg="Sorry! There was a problem accessing the COA validation server.", is_server_connection_err=True )
        
        if not response.status == self.STATUS_OK_200:
            return ValidationResponse(expense_code_str, ec_str_digits_only, is_valid=False, msg="Bad server response status: %s" % response.status)
            
        resp_data = response.read()
        
        is_valid, possible_err_msg = self.get_response_from_xml(resp_data)

        return ValidationResponse(expense_code_str, ec_str_digits_only, is_valid=is_valid, msg=possible_err_msg)
        
    
    def get_response_from_xml(self, response_xml_str):
        """Parse the XML response which has this format:
        <?xml version="1.0"?>
        <root>
            <ValidateGLAccountResponse>
                <ValidationFlag>Y</ValidationFlag>
                <ErrorMessage>null</ErrorMessage>
            </ValidateGLAccountResponse>
        </root>        
        
        return (True, 'VALID') or (False, "Error Message")
        """        
        if response_xml_str is None:
            return (False, 'XML string is None')

        try:
            res_dom = minidom.parseString(response_xml_str)
        except:
            return (False, 'Failed to validate XML')

        validate_gl_account_response = ''
        try:
            validate_gl_account_response = res_dom.getElementsByTagName("ValidateGLAccountResponse")[0]
            validation_flag = validate_gl_account_response.getElementsByTagName('ValidationFlag')[0].firstChild.nodeValue
        except IndexError:
            return (False, 'Bad XML response.  ValidateGLAccountResponse or ValidationFlag not found.')

        if validation_flag == 'Y':
            res_dom.unlink()
            return (True, 'VALID')

        try:
            error_message = validate_gl_account_response.getElementsByTagName('ErrorMessage')[0].firstChild.nodeValue
        except IndexError:
            return (False, 'Bad XML response.  ErrorMessage not found')

        res_dom.unlink()
        return (False, error_message)

    
        
    def get_xml_request(self, ec_str):
        if ec_str is None or not len(ec_str) == 33:
            return None
        
        return """<?xml version="1.0"?><ValidateGLAccountRequest>
       <Tub>%s</Tub>
       <Org>%s</Org>
       <Object>%s</Object>
       <Fund>%s</Fund>
       <Activity>%s</Activity>
       <Subactivity>%s</Subactivity>
       <Root>%s</Root>
       </ValidateGLAccountRequest>""" % (ec_str[0:3]\
                , ec_str[3:8]\
                , ec_str[8:12]\
                , ec_str[12:18]\
                , ec_str[18:24]\
                , ec_str[24:28]\
                , ec_str[28:33]\
            )
        



def validate_expense_code(is_test=True, ec_xml=None):
    if ec_xml is None:
        ec_xml = """<?xml version="1.0"?><ValidateGLAccountRequest>
    <Tub>370</Tub><Org>00100</Org><Object>6010</Object><Fund>000001</Fund><Activity>799599</Activity><Subactivity>0000</Subactivity><Root>00000</Root></ValidateGLAccountRequest>"""
    headers = {"Content-type": "text/xml"}
    if is_test:
        server_conn = httplib.HTTPSConnection('-old-ye-server-34:8852')
        server_conn.request('POST', '/GLValidate/ValidateGLAccount', ec_xml, headers)
    else:
        server_conn = httplib.HTTPSConnection('-old-ye-server-34:8052')
        server_conn.request('POST', '/GLValidate/ValidateGLAccount', ec_xml, headers)
        
    response = server_conn.getresponse()
    resp_data = response.read()
    print resp_data

"""
curl --header "Content-type:text/xml" --data '<?xml version="1.0"?><ValidateGLAccountRequest><Tub>370</Tub><Org>31570</Org><Object>7980</Object><Fund>132585</Fund><Activity>339463</Activity><Subactivity>0207</Subactivity><Root>44729</Root></ValidateGLAccountRequest>' https://apollo34.cadm.harvard.edu:8852/GLValidate/ValidateGLAccount


curl --header "Content-type:text/xml" --data '<?xml version="1.0"?><ValidateGLAccountRequest><Tub>370</Tub><Org>31570</Org><Object>7980</Object><Fund>132585</Fund><Activity>339463</Activity><Subactivity>0207</Subactivity><Root>44729</Root></ValidateGLAccountRequest>' https://apollo36.cadm.harvard.edu:8052/GLValidate/ValidateGLAccount
"""
#https://apollo36.cadm.harvard.edu:8052/GLValidate/ValidateGLAccount

if __name__ == '__main__':
    #validate_expense_code(batch_validation_url_test, ec_xml)
    ecv = ExpenseCodeValidator(use_test_server=True)
    vresp = ecv.validate_expense_code('370-31240-8550-130143-335272-0001-44050')
    print vresp.get_fmt_ec_str()
    print vresp
    
