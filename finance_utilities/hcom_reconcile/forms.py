from django import forms

class RequisitionEmailAdminForm(forms.ModelForm):

    class Meta:
        widgets = {  'description': forms.TextInput(attrs={'size': '100'})\
                    , 'notes': forms.Textarea(attrs={'rows': 5, 'cols':100}) \
                    , 'hcom_idnum' : forms.TextInput(attrs={'size': '30'})\
                  }
     
class RequisitionLineItemInlineForm(forms.ModelForm):
    class Meta:
        widgets = {  'description': forms.Textarea(attrs={'rows': 3, 'cols':40}) \
                    , 'charge_account': forms.TextInput(attrs={'size': 39}) \
                    , 'price': forms.TextInput(attrs={'size': 10}) \
                    , 'amount': forms.TextInput(attrs={'size': 10}) \
                    , 'line_num': forms.TextInput(attrs={'size': 4}) \
                }
                
                
class RequisitionLineItemAdminForm(forms.ModelForm):
    class Meta:
        widgets = {  'description': forms.Textarea(attrs={'rows': 2, 'cols':60}) \
                    , 'charge_account': forms.TextInput(attrs={'size': 39}) \
                    , 'price': forms.TextInput(attrs={'size': 10}) \
                    , 'amount': forms.TextInput(attrs={'size': 10}) \
                    , 'line_num': forms.TextInput(attrs={'size': 4}) \
                }

class PurchaseOrderLineItemInlineForm(forms.ModelForm):
    class Meta:
        widgets = {  'description': forms.Textarea(attrs={'rows': 3, 'cols':40}) \
                    #, 'charge_account': forms.TextInput(attrs={'size': 39}) \
                    , 'price': forms.TextInput(attrs={'size': 10}) \
                    , 'amount': forms.TextInput(attrs={'size': 10}) \
                    , 'line_num': forms.TextInput(attrs={'size': 4}) \
                    , 'rev': forms.TextInput(attrs={'size': 10}) \
                    , 'item_number': forms.TextInput(attrs={'size': 10}) \
                }

class PurchaseOrderAdminForm(forms.ModelForm):

    class Meta:
        widgets = {  'description': forms.TextInput(attrs={'size': '100'})\
                    , 'notes': forms.Textarea(attrs={'rows': 5, 'cols':100}) \
                    , 'hcom_idnum' : forms.TextInput(attrs={'size': '30'})\
                  }
                  
