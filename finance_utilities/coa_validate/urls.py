from django.conf.urls.defaults import *

urlpatterns = patterns(
    'finance_utilities.coa_validate.views'
,    url(r'^validate/$', 'view_ec_validation_form', name='view_ec_validation_form')

,    url(r'^define/$', 'view_define_ec_form', name='view_define_ec_form')

,    url(r'^mcb-roots/$', 'view_mcb_roots', name='view_mcb_roots')

,    url(r'^my-codes/$', 'view_my_codes', name='view_my_codes')


#,    url(r'^cf/trainee-emails/$', 'view_hcom_trainee_email_addresses', name='view_hcom_trainee_email_addresses')
,
)
