from django import forms
from finance_utilities.coa_validate.expense_code_validator import ExpenseCodeValidator, ValidationResponse, ExpenseCodeValidationResults
from django.conf import settings

MAX_EXPENSE_CODES_TO_VALIDATE = 20

class ExpenseCodeValidationForm(forms.Form):
    expense_codes = forms.CharField(label="Enter expense codes"\
            , help_text="(up to %s, in any format)" % MAX_EXPENSE_CODES_TO_VALIDATE\
            , widget=forms.Textarea(attrs={'rows':'5'\
                                , 'style':'width:400px'\
                                , 'class' : 'input-xlarge'\
                                , 'placeholder' : 'Note: object code "xxxx" changed to "6600"   Examples:     370-31330-8550-512701-600200-0000-50699    370.31570.xxxx.6244.736002.00000.044716   370|31560|xxxx|507210|600200|0000|00000   370313308550512701600200000050699     '\
                                })\
            )                    
            #, initial='examples: 370-31330-8550-512701-600200-0000-50699    370.31570.xxxx.6244.736002.00000.044716   370|31560|xxxx|507210|600200|0000|00000   370313308550512701600200000050699 '\
 
    def clean_expense_codes(self):
        expense_codes = self.cleaned_data.get('expense_codes', None)
        if expense_codes is None:
            raise forms.ValidationError("Please enter at least one expense code")

        expense_codes = expense_codes.encode('ascii', 'ignore')

        if str(expense_codes).strip() == '':
            raise forms.ValidationError("Please enter at least one expense code")

        return expense_codes
        
        
    def get_code_validation_results(self):
        expense_codes = self.cleaned_data.get('expense_codes', None)
        if expense_codes is None:
            return None
                
        ec_validator = ExpenseCodeValidator(use_test_server=settings.DEBUG)
        ec_results = []
        
        # remove strings less than 27 chars -- assume garbage
        potential_exp_codes = filter(lambda x: len(x) > 27, expense_codes.strip().split())
        
        for potential_ec in potential_exp_codes[0:MAX_EXPENSE_CODES_TO_VALIDATE]:
            vresp = ec_validator.validate_expense_code(potential_ec)
            ec_results.append(vresp)
            
        return ExpenseCodeValidationResults(ec_results)
        
