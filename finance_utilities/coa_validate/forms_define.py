from django import forms
from django.db.models import Q

from expense_code_definitions.models import *
from expense_code_definitions.ec_lookup import ExpenseCodeDefined, NOT_FOUND

import re

def digit_match(num_digits, val):
    """Valid values are None, empty string, or correct number of digits"""
    if val is None or val.strip()=='':
        return None
        
    if re.match('^\d{%s}$' % num_digits, val):
        return val    

    raise forms.ValidationError('Please enter a %s-digit code.' % num_digits)

class ExpenseCodeLookupForm(forms.Form):
    tub = forms.CharField(widget=forms.TextInput(attrs={'class':'input-mini', 'maxlength':3,'placeholder': '3 digits'}), required=False)
    org = forms.CharField(widget=forms.TextInput(attrs={'class':'input-mini', 'maxlength':5, 'placeholder': '5 digits'}), required=False)
    obj = forms.CharField(widget=forms.TextInput(attrs={'class':'input-small', 'maxlength':4, 'placeholder': '4 digits'}), required=False, label='Object')
    fund = forms.CharField(widget=forms.TextInput(attrs={'class':'input-mini','maxlength':6, 'placeholder': '6 digits'}), required=False)
    activity = forms.CharField(widget=forms.TextInput(attrs={'class':'input-mini', 'maxlength':6, 'placeholder': '6 digits'}), required=False)
    subactivity = forms.CharField(widget=forms.TextInput(attrs={'class':'input-mini','maxlength':4, 'placeholder': '4 digits'}), required=False, label='SubActivity')
    root = forms.CharField(widget=forms.TextInput(attrs={'class':'input-mini','maxlength':5, 'placeholder': '5 digits'}), required=False)

    def get_definitions(self):
        
        ecd = ExpenseCodeDefined(tub=self.clean_tub()\
                    ,org=self.clean_org()\
                    ,obj=self.clean_obj()\
                    ,fund=self.clean_fund()\
                    ,act=self.clean_activity()\
                    ,sub=self.clean_subactivity()\
                    ,root=self.clean_root()\
                )
        return ecd
      
    
    def clean(self):
        # If sub activity is entered, make sure activity is entered
        attrs = '''tub org obj fund activity subactivity root'''.split()
        val_found = False
        for attr in attrs:
            val = self.cleaned_data.get(attr, None)
            if val is not None:
                val_found = True
                break
        
        if not val_found:
            for attr in attrs[:1]:
                self._errors[attr] = ['Please enter at least one part of the expense code.',]
            raise forms.ValidationError('what?')#Please enter at least one part of the expense code.')
            
        return self.cleaned_data
                
    
    def clean_tub(self):
        return digit_match(3, self.cleaned_data["tub"])

    def clean_org(self):
        return digit_match(5, self.cleaned_data["org"])

    def clean_obj(self):
        return digit_match(4, self.cleaned_data["obj"])
        """
        val = self.cleaned_data["obj"]
        
        if val is None or val.strip()=='':
            return None
            
        if re.match('^(\d|x|X){4}$', val):
            return val    

        raise forms.ValidationError('Please enter a 4-character code.')
        """

    def clean_fund(self):
        return digit_match(6, self.cleaned_data["fund"])

    def clean_activity(self):
        return digit_match(6, self.cleaned_data["activity"])

    def clean_subactivity(self):
        return digit_match(4, self.cleaned_data["subactivity"])

    def clean_root(self):
        return digit_match(5, self.cleaned_data["root"])


