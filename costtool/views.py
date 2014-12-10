from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect,render, render_to_response
from django.db import IntegrityError
from django.template import Context, loader, RequestContext
from django.contrib.auth import authenticate, login as auth_login
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory

from costtool import models as m
from costtool.forms import PricesForm, UserForm, UserProfileForm, ProjectsForm, ProgramsForm, ProgramDescForm, ParticipantsForm, EffectForm,SettingsForm, GeographicalForm, GeographicalForm_orig, InflationForm, InflationForm_orig
import xlrd
import MySQLdb

def add_program(request):
    project_id = request.session['project_id']
    context = RequestContext(request)

    if request.method == 'POST':
        programform = ProgramsForm(request.POST)

        if programform.is_valid():
            progname = programform.save(commit=False)
            progname.projectId = project_id
            progname.save()
            return HttpResponseRedirect('/project/programs/'+project_id+'/program_list.html')
        else:
            print programform.errors

    else:
        programform = ProgramsForm()

    return render(request,
            'project/programs/add_program.html',
            {'programform': programform,'project_id':project_id})

def indices(request):
    project_id = request.session['project_id']
    return render(request,'project/indices.html',{'project_id':project_id})

def prices(request):
    return render(request,'prices/prices.html')

def imports(request):
    return render(request,'prices/imports.html')

def tabbedlayout(request,project_id,program_id):
    project = m.Projects.objects.get(pk=project_id)
    program = m.Programs.objects.get(pk=program_id)
    partform = ''
    try:
        programdesc = m.ProgramDesc.objects.get(programId=program_id)
        form1 = ProgramDescForm(request.POST, instance=programdesc)
        objectexists = True
    except ObjectDoesNotExist:
        form1 = ProgramDescForm(request.POST)
        objectexists = False
    
    PartFormSet = inlineformset_factory(m.ProgramDesc,m.ParticipantsPerYear,extra=10)
    if objectexists:
        try:
            partform = PartFormSet(request.POST,request.FILES, instance=programdesc,prefix="partform" )
            partobjexists = True
        except ObjectDoesNotExist:
            partform = PartFormSet(request.POST, request.FILES,prefix="partform")
            partobjexists = False
    else:
        partform = PartFormSet(request.POST, request.FILES,prefix="partform")
        partobjexists = False

    if partobjexists:
        partform = PartFormSet( instance=programdesc,prefix="partform")
    else:
        partform = PartFormSet(prefix="partform")   
 
    if request.method == 'POST':
        if form1.is_valid():
            numberofparticipants = form1.save(commit=False)
            numberofparticipants.numberofyears = 1
            numberofparticipants.programId = program
            numberofparticipants.save()
            programdesc = m.ProgramDesc.objects.get(pk=numberofparticipants.id)
            partform = PartFormSet(request.POST,request.FILES, instance=programdesc,prefix="partform" )
            if partform.is_valid():
                partform.save()
                programdesc.numberofyears=m.ParticipantsPerYear.objects.filter(programdescId=numberofparticipants.id).count()
                programdesc.save()
                return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html')
            else:
                print partform.errors
        else:
            print form1.errors
    else:
        if objectexists:
            form1 = ProgramDescForm(instance=programdesc)
        else:
            form1 = ProgramDescForm()
        
        if partobjexists:
            partform = PartFormSet( instance=programdesc, prefix="partform")
        else:
            partform = PartFormSet(prefix="partform")

    try:
        effect = m.Effectiveness.objects.get(programId=program_id)
        effectform = EffectForm(request.POST, instance=effect)
        effobjexists = True
    except ObjectDoesNotExist:
        effectform = EffectForm(request.POST)
        effobjexists = False
    
    if request.method == 'POST':
       if effectform.is_valid():
           sourceeffectdata = effectform.save(commit=False)
           sourceeffectdata.programId = program
           sourceeffectdata.save()
           return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html')
       else:
           print effectform.errors
    else:
        if effobjexists:
            effectform = EffectForm(instance=effect)
        else:
            effectform = EffectForm()

    return render (request,'project/programs/effect/tabbedview.html',{'project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform})

def program_list(request,project_id):
    request.session['project_id'] = project_id
    try:
        project = m.Projects.objects.get(pk=project_id)
        program = m.Programs.objects.filter(projectId=project_id)
    except ObjectDoesNotExist:
        return HttpResponse('Object does not exist!')
    return render_to_response(
            'project/programs/program_list.html',
            {'project':project,'program':program})

def index(request):
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    recent_projects = m.Projects.objects.filter(created_at__gt = two_days_ago).all()
    template = loader.get_template('index.html')
 
    context = Context({
        'projects_list' : recent_projects
    })
    return HttpResponse(template.render(context))

def project_detail(request, projects_id):
    try:
        project = m.Projects.objects.get(pk=projects_id)
    except m.Projects.DoesNotExist:
        raise Http404
    return render(request, 'projects/detail.html', {'projects':project})

def project_upload(request):
    if request.method == 'GET':
        return render(request, 'projects/upload.html', {})
    elif request.method == 'POST':
        project = m.Projects.objects.create(projectname=request.POST['projectname'],
                                            typeanalysis=request.POST['typeanalysis'],
                                            created_at=datetime.utcnow())
        return HttpResponseRedirect(reverse('project_detail', kwargs={'projects_id': projects.id}))       

def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=True)
            profile.user = user
            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'register/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect('/admin/costtool')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('login/login.html', {}, context)

def about(request):
    context = RequestContext(request)
    return render_to_response('about.html', {}, context)

def add_project(request):
    context = RequestContext(request)

    if request.method == 'POST':
        projectform = ProjectsForm(data=request.POST)

        if projectform.is_valid():
            projectname = projectform.save()
            projectname.save()
            return HttpResponseRedirect('/project/project_list.html')
        else:
            print projectform.errors

    else:
        projectform = ProjectsForm()        

    return render_to_response(
            'project/add_project.html',
            {'projectform': projectform}, context)

def project_list(request):
    allprojects = m.Projects.objects.all()
    template = loader.get_template('project/project_list.html')
    context = Context({
        'allprojects' : allprojects
    })
    return HttpResponse(template.render(context))

def del_project(request, proj_id):
    context = RequestContext(request)
    m.Projects.objects.get(pk=proj_id).delete()
    return HttpResponseRedirect('/project/project_list.html')

def add_price(request):
    context = RequestContext(request)
    if request.method == 'POST':
        pricesform = PricesForm(data=request.POST)

        if pricesform.is_valid():
            priceProvider = pricesform.save(commit=False)
            priceProvider.priceProvider = 'User'
            priceProvider.save()
            return HttpResponseRedirect('/prices/my_price_list.html')
        else:
            print priceform.errors

    else:
        pricesform = PricesForm()

    return render_to_response(
            'prices/add_price.html',
            {'pricesform': pricesform}, context)

def view_price(request, price_id):
    price = m.Prices.objects.get(pk=price_id)

    template = loader.get_template('prices/view_price.html')
    context = Context({
        'price' : price
    })
    return HttpResponse(template.render(context))

def edit_price(request, price_id):
    price = m.Prices.objects.get(pk=price_id)
    context = RequestContext(request)

    if request.method == 'POST':
        pricesform = PricesForm(request.POST,instance=price)
        if pricesform.is_valid():
            priceProvider = pricesform.save()
            priceProvider.save()
            return HttpResponseRedirect('/prices/my_price_list.html')
        else:
            print priceform.errors
    else:
        pricesform = PricesForm(instance=price)

    return render_to_response(
            'prices/edit_price.html',
            {'pricesform': pricesform}, context)

def del_price(request, price_id):
    context = RequestContext(request)
    m.Prices.objects.get(pk=price_id).delete()
    return HttpResponseRedirect('/prices/my_price_list.html')

def clear_prices(request):
    context = RequestContext(request)
    m.Prices.objects.filter(priceProvider='User').delete()
    return HttpResponseRedirect('/prices/my_price_list.html')

def price_list(request):
    allprices = m.Prices.objects.filter(priceProvider='CBCSE')

    template = loader.get_template('prices/price_list.html')
    context = Context({'allprices' : allprices})
    return HttpResponse(template.render(context))

def my_price_list(request):
    allprices2 = m.Prices.objects.filter(priceProvider='User')

    template = loader.get_template('prices/my_price_list.html')
    context = Context({'allprices2' : allprices2})
    return HttpResponse(template.render(context))

def import_excel(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/users/amritha/documents/DBofPrices.xls")
    sheet = book.sheet_by_name("Ingredients")

    # Establish a MySQL connection
    database = MySQLdb.connect (host="localhost", user = "root", passwd = "", db = "costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_prices (priceProvider,category,ingredient,edLevel,sector,descriptionPrice,unitMeasurePrice,price,yearPrice,statePrice,areaPrice,sourcePriceData,urlPrice,lastChecked,nextCheckDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        priceProvider      = sheet.cell(r,0).value
        category  = sheet.cell(r,1).value
        ingredient          = sheet.cell(r,2).value
        edLevel     = sheet.cell(r,3).value
        sector       = sheet.cell(r,4).value
        descriptionPrice = sheet.cell(r,5).value
        unitMeasurePrice        = sheet.cell(r,6).value
        price       = sheet.cell(r,7).value
        yearPrice     = sheet.cell(r,8).value
        statePrice        = sheet.cell(r,9).value
        areaPrice         = sheet.cell(r,10).value
        sourcePriceData          = sheet.cell(r,11).value
        urlPrice   = sheet.cell(r,12).value
        lastChecked   = sheet.cell(r,13).value
        nextCheckDate   = sheet.cell(r,14).value

        # Assign values from each row
        values = (priceProvider,category,ingredient,edLevel,sector,descriptionPrice,unitMeasurePrice,price,yearPrice,statePrice,areaPrice,sourcePriceData,urlPrice,lastChecked,nextCheckDate)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/prices/imports.html')

def import_geo(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/users/amritha/documents/GeographicalIndex.xlsx")
    sheet = book.sheet_by_name("Sheet1")

    # Establish a MySQL connection
    database = MySQLdb.connect (host="localhost", user = "root", passwd = "", db = "costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_geographicalindices_orig (stateIndex, areaIndex, geoIndex) VALUES (%s, %s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        stateIndex      = sheet.cell(r,0).value
        areaIndex  = sheet.cell(r,1).value
        geoIndex          = sheet.cell(r,2).value
        
        # Assign values from each row
        values = (stateIndex, areaIndex, geoIndex)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query    
    query = """INSERT INTO costtool_geographicalindices (stateIndex, areaIndex, geoIndex) VALUES (%s, %s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        stateIndex      = sheet.cell(r,0).value
        areaIndex  = sheet.cell(r,1).value
        geoIndex          = sheet.cell(r,2).value
        
        # Assign values from each row        
        values = (stateIndex, areaIndex, geoIndex)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/prices/imports.html')

def import_inf(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/users/amritha/documents/InflationIndex.xlsx")
    sheet = book.sheet_by_name("Sheet1")

    # Establish a MySQL connection
    database = MySQLdb.connect (host="localhost", user = "root", passwd = "", db = "costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_inflationindices_orig (yearCPI, indexCPI) VALUES (%s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        yearCPI      = sheet.cell(r,0).value
        indexCPI  = sheet.cell(r,1).value

        # Assign values from each row
        values = (yearCPI, indexCPI)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query    
    query = """INSERT INTO costtool_inflationindices (yearCPI, indexCPI) VALUES (%s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        yearCPI      = sheet.cell(r,0).value
        indexCPI  = sheet.cell(r,1).value

        # Assign values from each row
        values = (yearCPI, indexCPI)

        # Execute sql Query
        cursor.execute(query, values)

    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/prices/imports.html')

def add_settings(request,project_id):
    request.session['project_id'] = project_id
    context = RequestContext(request)
    try:
       setrec = m.Settings.objects.get(projectId=project_id)
       objectexists = True
    except ObjectDoesNotExist:
       objectexists = False
    
    if request.method == 'POST':
        if objectexists:
           setform = SettingsForm(request.POST, instance=setrec)
        else:
           setform = SettingsForm(request.POST)
        
        if setform.is_valid():
            discountRateEstimates = setform.save(commit=False)
            discountRateEstimates.projectId = project_id
            discountRateEstimates.save()
            return HttpResponseRedirect('/project/project_list.html')
        else:
            print setform.errors

    else:
        if objectexists:
           setform = SettingsForm(instance=setrec)
        else:
           setform = SettingsForm()

    return render_to_response(
            'project/add_settings.html',
            {'frm1': setform}, context)

def addedit_inf(request):
    InfFormSet = modelformset_factory(m.InflationIndices,extra=20)
    context = RequestContext(request)

    if request.method == 'POST':
       infform = InfFormSet(request.POST,request.FILES)

       if infform.is_valid():
          infform.save()
          return HttpResponseRedirect('/project/inflation.html')
       else:
          print infform.errors
    else:
        infform = InfFormSet()

    return render_to_response ('project/inflation.html',{'infform':infform},context)

def restore_inf(request):
    context = RequestContext(request)
    m.InflationIndices.objects.all().delete()
    for e in m.InflationIndices_orig.objects.all():
        m.InflationIndices.objects.create(yearCPI = e.yearCPI,indexCPI = e.indexCPI)
    return HttpResponseRedirect('/project/inflation.html')

def addedit_geo(request):
    GeoFormSet = modelformset_factory(m.GeographicalIndices,extra=20)
    context = RequestContext(request)

    if request.method == 'POST':
       geoform = GeoFormSet(request.POST,request.FILES)

       if geoform.is_valid():
          geoform.save()
          return HttpResponseRedirect('/project/geo.html')
       else:
          print geoform.errors
    else:
        geoform = GeoFormSet()

    return render_to_response ('project/geo.html',{'geoform':geoform},context) 

def restore_geo(request):
    context = RequestContext(request)
    m.GeographicalIndices.objects.all().delete()
    for e in m.GeographicalIndices_orig.objects.all():
        m.GeographicalIndices.objects.create(stateIndex = e.stateIndex,areaIndex = e.areaIndex, geoIndex = e.geoIndex )
    return HttpResponseRedirect('/project/geo.html')
