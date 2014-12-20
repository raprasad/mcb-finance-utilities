from django.conf.urls.defaults import *

urlpatterns = patterns(
    'finance_utilities.hcom_training.views'
,    url(r'^cf/(?P<trainee_id>(\w){32})/$', 'view_hcom_confirmation', name='view_hcom_confirmation')
,    url(r'^cf/trainee-emails/$', 'view_hcom_trainee_email_addresses', name='view_hcom_trainee_email_addresses')
,
)

urlpatterns += patterns(
    'finance_utilities.hcom_training.views_xls'
,    url(r'^trainee-xls/$', 'view_hcom_trainee_xls', name='view_hcom_trainee_xls')
,
)
