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
from costtool.forms import PricesForm, PricesSearchForm, PriceIndicesForm, WageDefaults, WageConverter, PriceBenefits, PriceSummary,MultipleSummary, UserForm, UserProfileForm, ProjectsForm, ProgramsForm, ProgramDescForm, ParticipantsForm, EffectForm,SettingsForm, GeographicalForm, GeographicalForm_orig, InflationForm, InflationForm_orig
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
    request.session['program_id'] = program_id
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
                request.session['programdescId'] = programdesc.id
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

    IngFormSet = modelformset_factory(m.Ingredients,extra=20)
    context = RequestContext(request)

    if request.method == 'POST':
       ingform = IngFormSet(request.POST,request.FILES)

       if ingform.is_valid():
          ingform.save()
          return HttpResponseRedirect('/project/programs/effect/'+ project_id +'/'+ program_id +'/tabbedview.html')
       else:
          print ingform.errors
    else:
        ingform = IngFormSet()


    return render (request,'project/programs/effect/tabbedview.html',{'project':project,'program':program,'frm1':form1,'partform':partform, 'frm2':effectform, 'frm3':ingform})

def search_costs(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']

    if 'hrsCalendarYr' in request.session:
        del request.session['hrsCalendarYr']

    if 'hrsAcademicYr' in request.session:
        del request.session['hrsAcademicYr']

    if 'hrsHigherEdn' in request.session:
        del request.session['hrsHigherEdn']

    if 'price' in request.session:
        del request.session['price']

    if 'measure' in request.session:
        del request.session['measure']

    if 'new_price' in request.session:
        del request.session['new_price']

    if 'new_measure' in request.session:
        del request.session['new_measure']

    if 'price_id' in request.session:
        del request.session['price_id']

    if 'Rate' in request.session:
        del request.session['Rate']

    if 'benefit_id' in request.session:
        del request.session['benefit_id']

    if 'search_cat' in request.session:
       del request.session['search_cat']

    if 'search_edLevel' in request.session:
       del request.session['search_edLevel']

    if 'search_sector' in request.session:
       del request.session['search_sector']
    
    if 'search_ingredient' in request.session:
       del request.session['search_ingredient']

    if request.method == 'POST':
        costform = PricesSearchForm(data=request.POST)
        if costform.is_valid():
            priceProvider = costform.save(commit=False)
            return HttpResponseRedirect('/project/programs/costs/price_search_results.html')
        else:
            print costform.errors
            return HttpResponse(costform.errors)
    else:
       costform = PricesSearchForm()
    return render_to_response('project/programs/costs/search_costs.html',{'costform':costform,'project_id':project_id, 'program_id':program_id},context)

def price_search(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']

    if 'category' in request.GET or 'edlevel' in request.GET or 'sector' in request.GET or 'ingredient' in request.GET:
       cat = request.GET['category']
       request.session['search_cat'] = cat
       edLevel = request.GET['edLevel']
       request.session['search_edLevel'] = edLevel 
       sector = request.GET['sector']
       request.session['search_sector'] = sector
       ingredient = request.GET['ingredient']
       request.session['search_ingredient'] = ingredient
       kwargs = { }
       if cat:
          kwargs['category'] = cat
       if edLevel:
          kwargs['edLevel'] = edLevel
       if sector:
          kwargs['sector'] = sector
       if ingredient:
          kwargs['ingredient'] = ingredient
       prices = m.Prices.objects.filter(**kwargs)
       pcount = prices.count()
       template = loader.get_template('project/programs/costs/price_search_results.html')
       context = Context({'prices' : prices, 'pcount':pcount, 'cat': cat, 'edLevel':edLevel, 'sector':sector, 'ingredient':ingredient, 'project_id':project_id, 'program_id':program_id})
       return HttpResponse(template.render(context))
    else:
        return HttpResponse('Please enter some criteria to do a search')

def price_indices(request,price_id):
    price = m.Prices.objects.get(pk=price_id)
    project_id = request.session['project_id']
    program_id = request.session['program_id']

    cat =  request.session['search_cat']
    edLevel =  request.session['search_edLevel']
    sector =  request.session['search_sector']
    ingredient = request.session['search_ingredient']

    if 'new_price' in request.session:
       new_price = float(request.session['new_price'])
    else:
       new_price = 0.0
       request.session['new_price'] = 0.0

    if 'new_measure' in request.session:
       new_measure = request.session['new_measure']
    else:
       new_measure = 'Hour'
       request.session['new_measure'] = 'Hour'
 
    request.session['price_id'] = price_id
    request.session['price'] = price.price
    request.session['measure'] = price.unitMeasurePrice
    template = loader.get_template('project/programs/costs/price_indices.html')
    context = Context({
        'price' : price,
        'new_price' : new_price,
        'new_measure' : new_measure,
        'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient, 
        'project_id':project_id, 'program_id':program_id 
    })
    return HttpResponse(template.render(context))

def nonper_indices(request,price_id):
    price = m.Prices.objects.get(pk=price_id)
    project_id = request.session['project_id']
    program_id = request.session['program_id']

    cat =  request.session['search_cat']
    edLevel =  request.session['search_edLevel']
    sector =  request.session['search_sector']
    ingredient = request.session['search_ingredient']

    if 'new_price' in request.session:
       new_price = float(request.session['new_price'])
    else:
       new_price = 0.0
       request.session['new_price'] = 0.0

    if 'new_measure' in request.session:
       new_measure = request.session['new_measure']
    else:
       new_measure = 'Hour'
       request.session['new_measure'] = 'Hour'

    request.session['price_id'] = price_id
    request.session['price'] = price.price
    request.session['measure'] = price.unitMeasurePrice
    template = loader.get_template('project/programs/costs/nonper_indices.html')
    context = Context({
        'price' : price,
        'new_price' : new_price,
        'new_measure' : new_measure,
        'cat' : cat, 'edLevel':  edLevel, 'sector': sector,'ingredient' : ingredient,
        'project_id':project_id, 'program_id':program_id
    })
    return HttpResponse(template.render(context))

def wage_converter(request):
    context = RequestContext(request)
    price_id = request.session['price_id']

    if 'price' in request.session:
       price = float(request.session['price'])
    else:
       price = 0.0
       request.session['price'] = 0.0

    if 'measure' in request.session:
       measure = request.session['measure'] 
    else:
       measure = ''
       request.session['measure'] = ''

    project_id = request.session['project_id']
    if 'hrsCalendarYr' in request.session:
       hrsCalendarYr = request.session['hrsCalendarYr']
    else:
        try:
            sett = m.Settings.objects.get(projectId=project_id)
            hrsCalendarYr = sett.hrsCalendarYr
            request.session['hrsCalendarYr'] = hrsCalendarYr
            objExists = True
        except ObjectDoesNotExist:
            hrsCalendarYr = 2080
            request.session['hrsCalendarYr'] = hrsCalendarYr
            objExists = False

    if 'hrsAcademicYr' in request.session:
       hrsAcademicYr = request.session['hrsAcademicYr']
    else:
        if objExists:
            hrsAcademicYr = sett.hrsAcademicYr
            request.session['hrsAcademicYr'] = hrsAcademicYr
        else:
            hrsAcademicYr = 1440
            request.session['hrsAcademicYr'] = hrsAcademicYr

    if 'hrsHigherEdn' in request.session:
       hrsHigherEdn = request.session['hrsHigherEdn']
    else:
        if objExists:
            hrsHigherEdn = sett.hrsHigherEdn
            request.session['hrsHigherEdn'] = hrsHigherEdn
        else:
            hrsHigherEdn = 1560
            request.session['hrsHigherEdn'] = hrsHigherEdn

    hrsCalendarYr = float(hrsCalendarYr)
    hrsAcademicYr = float(hrsAcademicYr)
    hrsHigherEdn = float(hrsHigherEdn)

    if 'new_price' in request.session:
        new_price = request.session['new_price']
    else:  
        new_price = 0.0
        request.session['new_price'] = 0.0

    if 'new_measure' in request.session:
        new_measure = request.session['new_measure']
    else:  
        new_measure = 'Hour'
        request.session['new_measure'] = 'Hour'

    if request.method == 'POST':
        if 'compute' in request.POST:
            form = WageConverter(data=request.POST)
            if form.is_valid():
                newMeasure = form.save(commit=False)
                if measure == 'Hour':
                    newMeasure.convertedPrice = price 
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price * 8
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price * 40
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * hrsCalendarYr
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * hrsAcademicYr
                    if newMeasure.newMeasure == 'Higher Ed Academic Year':
                        newMeasure.convertedPrice = price * hrsHigherEdn

                if measure == 'Day': 
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price /  8
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price *  5
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / 8)
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / 8)
                    if newMeasure.newMeasure == 'Higher Ed Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / 8)

                if measure == 'Week': 
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / 40
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price /  5
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * 52
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * 36
                    if newMeasure.newMeasure == 'Higher Ed Academic Year':
                        newMeasure.convertedPrice = price * 39

                if measure == 'Calendar Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / hrsCalendarYr
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price / (hrsCalendarYr / 8)
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price / 52
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / hrsCalendarYr)
                    if newMeasure.newMeasure == 'Higher Ed Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / hrsCalendarYr)

                if measure == 'K-12 Academic Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / hrsAcademicYr
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price / (hrsAcademicYr / 8)
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price / 36
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / hrsAcademicYr)
                    if newMeasure.newMeasure == 'Higher Ed Academic Year':
                        newMeasure.convertedPrice = price * (hrsHigherEdn / hrsAcademicYr)

                if measure == 'Higher Ed Academic Year':
                    newMeasure.convertedPrice = price
                    if newMeasure.newMeasure == 'Hour':
                        newMeasure.convertedPrice = price / hrsHigherEdn
                    if newMeasure.newMeasure == 'Day':
                        newMeasure.convertedPrice = price / (hrsHigherEdn / 8)
                    if newMeasure.newMeasure == 'Week':
                        newMeasure.convertedPrice = price / 39
                    if newMeasure.newMeasure == 'Calendar Year':
                        newMeasure.convertedPrice = price * (hrsCalendarYr / hrsHigherEdn)
                    if newMeasure.newMeasure == 'K-12 Academic Year':
                        newMeasure.convertedPrice = price * (hrsAcademicYr / hrsHigherEdn)

                request.session['new_price'] = newMeasure.convertedPrice
                request.session['new_measure'] = newMeasure.newMeasure 
                return HttpResponseRedirect('/project/programs/costs/wage_converter.html')
            else:
                print form.errors

        if 'use' in request.POST:
            price_id = request.session['price_id']
            return HttpResponseRedirect('/project/programs/costs/'+ price_id + '/price_indices.html')

    else:
        form = WageConverter(initial={'convertedPrice':new_price,'newMeasure':new_measure})

    return render_to_response('project/programs/costs/wage_converter.html',{'form':form, 'convertedPrice':new_price,'newMeasure':new_measure,'price':price, 'price_id':price_id,'measure':measure, 'hrsCalendarYr': hrsCalendarYr, 'hrsAcademicYr':hrsAcademicYr, 'hrsHigherEdn':hrsHigherEdn},context)
 
def wage_defaults(request):
    context = RequestContext(request)

    if 'hrsCalendarYr' in request.session:
       hrsCalendarYr = request.session['hrsCalendarYr']
    else:   
        try:
            sett = m.Settings.objects.get(projectId=project_id)
            hrsCalendarYr = sett.hrsCalendarYr
            objExists = True 
        except ObjectDoesNotExist:
            hrsCalendarYr = 2080
            objExists = False

    if 'hrsAcademicYr' in request.session:
       hrsAcademicYr = request.session['hrsAcademicYr']
    else:
        if objExists:
            hrsAcademicYr = sett.hrsAcademicYr
        else:
            hrsAcademicYr = 1440

    if 'hrsHigherEdn' in request.session:
       hrsHigherEdn = request.session['hrsHigherEdn']
    else:
        if objExists:
            hrsHigherEdn = sett.hrsHigherEdn
        else:
            hrsHigherEdn = 1560
 
    if request.method == 'POST':
        form = WageDefaults(data=request.POST)
        if form.is_valid():
            benefitRate = form.save(commit=False)
            request.session['hrsCalendarYr'] = benefitRate.hrsCalendarYr
            request.session['hrsAcademicYr'] = benefitRate.hrsAcademicYr
            request.session['hrsHigherEdn'] = benefitRate.hrsHigherEdn
            return HttpResponseRedirect('/project/programs/costs/wage_converter.html')
        else:
            print form.errors
    else:
       form = WageDefaults(initial={'hrsCalendarYr': hrsCalendarYr, 'hrsAcademicYr':hrsAcademicYr, 'hrsHigherEdn':hrsHigherEdn}) 

    return render_to_response('project/programs/costs/wage_defaults.html',{'form':form},context)

def price_benefits(request,price_id):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    request.session['price_id'] = price_id
    request.session['Rate'] = 3
    price = m.Prices.objects.get(pk=price_id)
    
    if 'benefit_id' in request.session:
        benefit_id = request.session['benefit_id']
        benefit = m.Benefits.objects.get(pk=benefit_id)
        BenefitRate = benefit.BenefitRate
    else:
        BenefitRate = request.session['Rate']

    if request.method == 'POST':
        form = PriceBenefits(request.POST)
        if form.is_valid():
            benefitRate = form.save(commit=false)
            request.session['YN'] = benefitRate.benefitRateYN
            request.session['Rate'] = benefitRate.benefitRate
            return HttpResponseRedirect('project/programs/costs/summary.html')
        else:
            print form.errors

    else:
        form = PriceBenefits(initial={'benefitRate':BenefitRate})
    return render_to_response('project/programs/costs/price_benefits.html',{'form':form, 'price':price, 'project_id':project_id, 'program_id':program_id},context)

def benefits(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''
    allbenefits = m.Benefits.objects.all()
    return render(request,'project/programs/costs/benefits.html', {'project_id':project_id, 'program_id':program_id, 'allbenefits' : allbenefits, 'price_id':price_id})

def save_benefit(request,ben_id):
    context = RequestContext(request)
    request.session['benefit_id'] = ben_id
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''
    return HttpResponseRedirect('/project/programs/costs/'+ price_id +'/price_benefits.html')

def price_summary(request):
    context = RequestContext(request)
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''

    if 'YN' in request.session:
       YN = request.session['YN']
    else:
       YN = 'N'

    if 'Rate' in request.session:
       Rate = request.session['Rate']
    else:
       Rate = ''

    if 'new_price' in request.session:
       new_price = request.session['new_price']
    else:
       new_price = 0.0

    if 'new_measure' in request.session:
       new_measure = request.session['new_measure']
    else:
       new_measure = 'Hour'

    project_id = request.session['project_id']
    program_id = request.session['program_id']

    pcount = 0

    if 'programdescId' in request.session:
       programdescId = request.session['programdescId']
       pcount = m.ParticipantsPerYear.objects.filter(programdescId_id=programdescId).count()

    price = m.Prices.objects.get(pk=price_id)
    if 'benefit_id' in request.session:
        benefit = m.Benefits.objects.get(pk=request.session['benefit_id'])
        SourceBenefitData = benefit.SourceBenefitData
    else:
        SourceBenefitData = ''
    inf = m.InflationIndices.objects.filter(yearCPI=price.yearPrice)
    if pcount > 0:
       MFormSet = modelformset_factory(m.Ingredients, extra=pcount)
       if request.method == 'POST':
          form = MFormSet(request.POST, request.FILES)
          if form.is_valid():
             ingredients = form.save(commit=False)
             for ingredient in ingredients:
                 ingredient.category = price.category
                 ingredient.ingredient = price.ingredient
                 ingredient.edLevel = price.edLevel
                 ingredient.sector = price.sector
                 ingredient.unitMeasurePrice = price.unitMeasurePrice
                 ingredient.price = price.price
                 ingredient.sourcePriceData = price.sourcePriceData
                 ingredient.urlPrice = price.urlPrice
                 ingredient.newMeasure = request.session['new_measure']
                 ingredient.convertedPrice = request.session['new_price']
                 ingredient.benefitYN = YN
                 ingredient.benefitRate = request.session['Rate']
                 ingredient.SourceBenefitData = SourceBenefitData
                 ingredient.yearPrice = price.yearPrice
                 ingredient.statePrice = price.statePrice
                 ingredient.areaPrice = price.areaPrice
                 ingredient.programId = request.session['program_id']
                 ingredient.save()

             return HttpResponseRedirect('/project/programs/costs/finish.html')

          else:
             print form.errors

       else:
          form = MFormSet(queryset=m.Ingredients.objects.none())
    else:
       if request.method == 'POST':
          form = PriceSummary(request.POST)
          if form.is_valid():
             ingredient = form.save(commit=False)
             ingredient.category = price.category
             ingredient.ingredient = price.ingredient
             ingredient.edLevel = price.edLevel
             ingredient.sector = price.sector
             ingredient.unitMeasurePrice = price.unitMeasurePrice
             ingredient.price = price.price
             ingredient.sourcePriceData = price.sourcePriceData
             ingredient.urlPrice = price.urlPrice
             ingredient.newMeasure = request.session['new_measure']
             ingredient.convertedPrice = request.session['new_price']
             ingredient.benefitYN = YN
             ingredient.benefitRate = request.session['Rate']
             ingredient.SourceBenefitData = SourceBenefitData
             ingredient.yearPrice = price.yearPrice
             ingredient.statePrice = price.statePrice
             ingredient.areaPrice = price.areaPrice
             ingredient.programId = request.session['program_id']
             ingredient.save()
             return HttpResponseRedirect('/project/programs/costs/finish.html')
          else:
             print form.errors

       else:
          form = PriceSummary()
    return render_to_response('project/programs/costs/summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure},context)
 
def nonper_summary(request):
    context = RequestContext(request)
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''

    if 'YN' in request.session:
       YN = request.session['YN']
    else:
       YN = 'N'

    if 'Rate' in request.session:
       Rate = request.session['Rate']
    else:
       Rate = ''

    if 'new_price' in request.session:
       new_price = request.session['new_price']
    else:
       new_price = 0.0
 
    if 'new_measure' in request.session:
       new_measure = request.session['new_measure']
    else:
       new_measure = 'Hour'

    project_id = request.session['project_id']
    program_id = request.session['program_id']

    pcount = 0

    if 'programdescId' in request.session:
       programdescId = request.session['programdescId']
       pcount = m.ParticipantsPerYear.objects.filter(programdescId_id=programdescId).count()
    
    price = m.Prices.objects.get(pk=price_id)
    inf = m.InflationIndices.objects.filter(yearCPI=price.yearPrice)
    if pcount > 0:
       MFormSet = modelformset_factory(m.Ingredients, extra=pcount)
       if request.method == 'POST':
          form = MFormSet(request.POST, request.FILES)
          if form.is_valid():
             ingredients = form.save(commit=False)
             for ingredient in ingredients:
                 ingredient.category = price.category
                 ingredient.ingredient = price.ingredient
                 ingredient.edLevel = price.edLevel
                 ingredient.sector = price.sector
                 ingredient.unitMeasurePrice = price.unitMeasurePrice
                 ingredient.price = price.price
                 ingredient.sourcePriceData = price.sourcePriceData
                 ingredient.urlPrice = price.urlPrice
                 ingredient.newMeasure = request.session['new_measure']
                 ingredient.convertedPrice = request.session['new_price']
                 ingredient.yearPrice = price.yearPrice
                 ingredient.statePrice = price.statePrice
                 ingredient.areaPrice = price.areaPrice
                 ingredient.programId = request.session['program_id']
                 ingredient.save()

             return HttpResponseRedirect('/project/programs/costs/finish.html')
          else:
             print form.errors

       else:
          form = MFormSet(queryset=m.Ingredients.objects.none())
    else:
       if request.method == 'POST':
          form = PriceSummary(request.POST)
          if form.is_valid():
             ingredient = form.save(commit=False)
             ingredient.category = price.category
             ingredient.ingredient = price.ingredient
             ingredient.edLevel = price.edLevel
             ingredient.sector = price.sector
             ingredient.unitMeasurePrice = price.unitMeasurePrice
             ingredient.price = price.price
             ingredient.sourcePriceData = price.sourcePriceData
             ingredient.urlPrice = price.urlPrice        
             ingredient.newMeasure = request.session['new_measure']
             ingredient.convertedPrice = request.session['new_price']
             ingredient.yearPrice = price.yearPrice
             ingredient.statePrice = price.statePrice
             ingredient.areaPrice = price.areaPrice
             ingredient.programId = request.session['program_id']
             ingredient.save()
             return HttpResponseRedirect('/project/programs/costs/finish.html')
          else:
             print form.errors

       else:
          form = PriceSummary()
    return render_to_response('project/programs/costs/nonper_summary.html',{'project_id':project_id, 'program_id':program_id, 'pcount':pcount,'form':form, 'price':price, 'Rate':Rate, 'new_price':new_price,'new_measure':new_measure},context)

def finish(request):
    context = RequestContext(request)
    project_id = request.session['project_id']
    program_id = request.session['program_id']
    if 'price_id' in request.session:
       price_id = request.session['price_id']
    else:
       price_id = ''
    price = m.Prices.objects.get(pk=price_id)
    return render(request,'project/programs/costs/finish.html', {'price':price, 'project_id':project_id, 'program_id':program_id})

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
    m.Prices.objects.filter(priceProvider='CBCSE').delete()

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
    m.GeographicalIndices_orig.objects.all().delete()
    m.GeographicalIndices.objects.all().delete()

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
    m.InflationIndices_orig.objects.all().delete()
    m.InflationIndices.objects.all().delete()

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

def import_benefits(request):
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/users/amritha/documents/Benefits.xlsx")
    sheet = book.sheet_by_name("Sheet1")
    m.Benefits.objects.all().delete()

    # Establish a MySQL connection
    database = MySQLdb.connect (host="localhost", user = "root", passwd = "", db = "costtool")

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Create the INSERT INTO sql query
    query = """INSERT INTO costtool_benefits (SectorBenefit, EdLevelBenefit, PersonnelBenefit, TypeRateBenefit,	YearBenefit, BenefitRate, SourceBenefitData, URLBenefitData) VALUES (%s, %s,%s, %s,%s, %s,%s, %s)"""

    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        SectorBenefit      = sheet.cell(r,0).value
        EdLevelBenefit  = sheet.cell(r,1).value
        PersonnelBenefit = sheet.cell(r,2).value
        TypeRateBenefit      = sheet.cell(r,3).value
        YearBenefit = sheet.cell(r,4).value
        BenefitRate  = sheet.cell(r,5).value
        SourceBenefitData      = sheet.cell(r,6).value
        URLBenefitData  = sheet.cell(r,7).value

        # Assign values from each row
        values = (SectorBenefit, EdLevelBenefit, PersonnelBenefit, TypeRateBenefit, YearBenefit, BenefitRate, SourceBenefitData, URLBenefitData)

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
