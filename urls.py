from django.conf.urls import patterns, include, url
from django.contrib import admin
from costtool import views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'costtool.views.index', name='index'),
    url(r'^projects/(?P<projects_id>\d+)/detail.html$',
        'costtool.views.project_detail', name='project_detail'),

    url(r'^projects/upload.html$', 'costtool.views.project_upload', name='project_upload'),

    url(r'^prices/add_price.html$', 'costtool.views.add_price', name='add_price'),
    url(r'^prices/price_list.html$', 'costtool.views.price_list', name='price_list'),
    url(r'^prices/(?P<price_id>\d+)/view_price.html$', 'costtool.views.view_price', name='view_price'),
    url(r'^prices/(?P<price_id>\d+)/edit_price.html$', 'costtool.views.edit_price', name='edit_price'),
    url(r'^prices/(?P<price_id>\d+)/del_price.html$', 'costtool.views.del_price', name='del_price'),

    url(r'^project/add_project.html$', 'costtool.views.add_project', name='add_project'),
    url(r'^project/project_list.html$', 'costtool.views.project_list', name='project_list'),
    url(r'^project/(?P<proj_id>\d+)/del_project.html$', 'costtool.views.del_project', name='del_project'),

    url(r'^project/(?P<project_id>\d+)/add_settings.html$', 'costtool.views.add_settings', name='add_settings'),
    url(r'^project/indices.html$', 'costtool.views.indices', name='indices'),
    url(r'^project/geo.html$', 'costtool.views.addedit_geo', name='addedit_geo'),
    url(r'^project/restore_geo.html$', 'costtool.views.restore_geo', name='restore_geo'),
    url(r'^project/inflation.html$', 'costtool.views.addedit_inf', name='addedit_inf'),
    url(r'^project/restore_inf.html$', 'costtool.views.restore_inf', name='restore_inf'),
    
    url(r'^project/programs/(?P<project_id>\d+)/program_list.html$','costtool.views.program_list', name='program_list'),

    url(r'^project/programs/add_program.html$', 'costtool.views.add_program', name='add_program'),

    url(r'^project/programs/effect/(?P<project_id>\d+)/(?P<program_id>\d+)/tabbedview.html$', 'costtool.views.tabbedlayout', name='tabbedlayout'),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^register/register.html$', 'costtool.views.register', name='register'), 
    url(r'^login/login.html$', 'costtool.views.user_login', name='user_login'),
    url(r'^about.html$', 'costtool.views.about', name='about'),
)

