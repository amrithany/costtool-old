from django.conf.urls import patterns, include, url
from django.contrib import admin
from costtool import views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'costtool.views.about', name='about'),
    url(r'^projects/(?P<projects_id>\d+)/detail.html$',
        'costtool.views.project_detail', name='project_detail'),

    url(r'^projects/upload.html$', 'costtool.views.project_upload', name='project_upload'),

    url(r'^prices/add_price.html$', 'costtool.views.add_price', name='add_price'),
    url(r'^prices/price_list.html$', 'costtool.views.price_list', name='price_list'),
    url(r'^prices/my_price_list.html$', 'costtool.views.my_price_list', name='my_price_list'),
    url(r'^prices/prices.html$', 'costtool.views.prices', name='prices'),
    url(r'^prices/imports.html$', 'costtool.views.imports', name='imports'),
    url(r'^prices/clear_prices.html$', 'costtool.views.clear_prices', name='clear_prices'),
    url(r'^prices/(?P<price_id>\d+)/view_price.html$', 'costtool.views.view_price', name='view_price'),
    url(r'^prices/(?P<price_id>\d+)/edit_price.html$', 'costtool.views.edit_price', name='edit_price'),
    url(r'^prices/(?P<price_id>\d+)/del_price.html$', 'costtool.views.del_price', name='del_price'),
    url(r'^prices/import_excel.html$', 'costtool.views.import_excel', name='import_excel'),
    url(r'^prices/import_geo.html$', 'costtool.views.import_geo', name='import_geo'),
    url(r'^prices/import_inf.html$', 'costtool.views.import_inf', name='import_inf'),
    url(r'^prices/import_benefits.html$', 'costtool.views.import_benefits', name='import_benefits'),

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

    url(r'^project/programs/costs/search_costs.html$', 'costtool.views.search_costs', name='search_costs'),
    url(r'^project/programs/costs/price_search_results.html$', 'costtool.views.price_search', name='price_search'),
    url(r'^project/programs/costs/(?P<price_id>\d+)/price_indices.html$', 'costtool.views.price_indices', name='price_indices'),
    url(r'^project/programs/costs/(?P<price_id>\d+)/nonper_indices.html$', 'costtool.views.nonper_indices', name='nonper_indices'),
    url(r'^project/programs/costs/(?P<price_id>\d+)/price_benefits.html$', 'costtool.views.price_benefits', name='price_benefits'),
    url(r'^project/programs/costs/benefits.html$', 'costtool.views.benefits', name='benefits'),
    url(r'^project/programs/costs/(?P<ben_id>\d+)/save_benefit.html$', 'costtool.views.save_benefit', name='save_benefit'),

    url(r'^project/programs/costs/wage_converter.html$', 'costtool.views.wage_converter', name='wage_converter'),
    url(r'^project/programs/costs/wage_defaults.html$', 'costtool.views.wage_defaults', name='wage_defaults'),
    url(r'^project/programs/costs/summary.html$', 'costtool.views.price_summary', name='price_summary'),

    url(r'^project/programs/costs/nonper_summary.html$', 'costtool.views.nonper_summary', name='nonper_summary'),
    url(r'^project/programs/costs/finish.html$', 'costtool.views.finish', name='finish'),
    url(r'^project/programs/costs/financial.html$', 'costtool.views.comp_table',  name='comp_table'),
    url(r'^project/programs/costs/umconverter.html$', 'costtool.views.um_converter', name='um_converter'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^register/register.html$', 'costtool.views.register', name='register'), 
    url(r'^login/login.html$', 'costtool.views.user_login', name='user_login'),
    url(r'^index.html$', 'costtool.views.index', name='index'),
)

