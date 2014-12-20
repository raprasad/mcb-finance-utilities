from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # 
    # HCOM  Training
    url(r'^hcom/', include('finance_utilities.hcom_training.urls')),
    
    url(r'^coa/', include('finance_utilities.coa_validate.urls')),
    
    # url(r'^$', 'finance_utilities.views.home', name='home'),
    # url(r'^finance_utilities/', include('finance_utilities.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^mcb-control-panel/', include(admin.site.urls)),
)
