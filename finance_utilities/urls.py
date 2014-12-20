from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

MCB_URL_PREFIX = 'finutil/'

urlpatterns = patterns('',
    # Examples:
    # 
    # HCOM  Training
    (r'^%shcom/'% MCB_URL_PREFIX, include('finance_utilities.hcom_training.urls')),
    
    # url(r'^$', 'finance_utilities.views.home', name='home'),
     url(r'^%scoa/' % MCB_URL_PREFIX, include('finance_utilities.coa_validate.urls')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #(r'^dfiles/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': '/Users/some-user/projects/mcb-git/mcb-finance-utilities/files_to_serve'}),
    (r'^dfiles/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': '/Users/some-user/mcb-git/mcb-finance-utilities/files_to_serve'}),

    # Uncomment the next line to enable the admin:
    url(r'^%smcb-control-panel/' % MCB_URL_PREFIX, include(admin.site.urls)),
)
urlpatterns += staticfiles_urlpatterns()