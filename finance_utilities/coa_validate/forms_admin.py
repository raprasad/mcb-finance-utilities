from django import forms
import re

def digit_match(num_digits, val):
    if re.match('^\d{%s}$' % num_digits, val):
        return val    
    raise forms.ValidationError('Please enter a %s-digit code.' % num_digits)


class CheckedExpenseCodeForm(forms.ModelForm):
    def clean_expense_code(self):
        return digit_match(33, self.cleaned_data["expense_code"])

    class Meta:
         widgets = {  'expense_code': forms.TextInput(attrs={'size': 33 })} 

