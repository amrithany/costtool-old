from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from costtool.models import UserProfile, Projects, Programs, ProgramDesc, ParticipantsPerYear, Effectiveness, Prices, Settings,GeographicalIndices, GeographicalIndices_orig, InflationIndices, InflationIndices_orig
from crispy_forms.bootstrap import *
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('organisation','position','licenseSigned','signed_at')

class ProjectsForm(forms.ModelForm):
    projectname  = forms.CharField(label="Project Name:",error_messages = {'required': "The Project Name is required"})
    typeanalysis  = forms.ChoiceField(choices=(('Cost Analysis','Cost Analysis'),
                                               ('Cost-Effectiveness Analysis', 'Cost-Effectiveness Analysis')), label="Type of Analysis:")
    typeofcost = forms.ChoiceField(choices=(('Total Costs', 'Total Costs'), ('Differential Costs', 'Differential Costs')),label="Are you considering?")

    class Meta:
        model = Projects
        fields = ('projectname','typeanalysis','typeofcost')

class SettingsForm(forms.ModelForm):
    choicesEdlevel = (('Select','Select all'), ('General','General'), ('Grades PK', 'Grades PK'), ('Grades K-6','Grades K-6'), ('Grades 6-8','Grades 6-8'),('Grades 9-12','Grades 9-12'),('Grades K-12', 'Grades K-12'), ('PostSecondary', 'PostSecondary'))
    choicesSector = (('Select', 'Select all'),('Any', 'Any sector'),('Private','Private'),('Public','Public'))
    choicesYear = (('All', 'See prices from all years'),('recent','See most recent prices only'))
    yrquery = InflationIndices.objects.values_list('yearCPI', flat=True).distinct()
    yrquery_choices =  [(id, id) for id in yrquery]
    iquery = GeographicalIndices.objects.values_list('stateIndex', flat=True).distinct()
    iquery_choices =  [(id, id) for id in iquery]
    areaquery = GeographicalIndices.objects.values_list('areaIndex', flat=True).distinct()
    areaquery_choices =  [(id, id) for id in areaquery]
    discountRateEstimates = forms.DecimalField(required=False,max_digits=6,decimal_places=2,min_value=0.01,initial=3,label="Discount Rate for programs in which costs are incurred over multiple years:")
    yearEstimates = forms.ChoiceField(yrquery_choices, required=False, widget=forms.Select(),label="In which year do you want to express costs?")
    stateEstimates  = forms.ChoiceField(iquery_choices, required=False, widget=forms.Select(), label="In which geographical location do you want to express costs?")
    areaEstimates = forms.ChoiceField(areaquery_choices, required=False, widget=forms.Select(), label="")
    selectDatabase = forms.MultipleChoiceField(choices=(('CBCSE','CBCSE Database of Educational Resource Prices'),('My','Database My Prices')),required=False,label="Select which database of prices you will use (can select more than one):", widget=forms.CheckboxSelectMultiple())
    limitEdn = forms.MultipleChoiceField(choices=choicesEdlevel,required=False,label="<strong>EDUCATIONAL LEVEL</strong>", widget=forms.CheckboxSelectMultiple())
    limitSector = forms.MultipleChoiceField(choices=choicesSector,required=False,label="<strong>SECTOR</strong>",widget=forms.CheckboxSelectMultiple())
    limitYear = forms.MultipleChoiceField(choices=choicesYear,required=False,label="<strong>YEAR</strong>",widget=forms.CheckboxSelectMultiple())
    hrsCalendarYr = forms.IntegerField(required=False,initial=2080,label="Number of hours in the calendar year: The calendar year consists of 2,080 working hours (52 weeks, 5 days a week, 8 hrs a day) according to the U.S. Bureau of Labor Statistics. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the calendar year in the following cell:")
    hrsAcademicYr = forms.IntegerField(required=False,initial=1440, label="Number of hours in the K-12 academic year: The academic year consists of 1,440 working hours (36 weeks, 5 days a week, 8 hrs a day) according to CBCSE. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the K-12 academic year in the following cell:")
    hrsHigherEdn = forms.IntegerField(required=False,initial=1560,label="Number of hours in the higher education academic year: The academic year consists of 1,560 working hours (39 weeks, 5 days a week, 8 hrs a day) according to CBCSE. This is used as the default number for the wage converter. However, if this number does not fit your requirements, you can enter a different number of hours for the higher education academic year in the following cell:")

    class Meta:
        model = Settings
        fields = ('discountRateEstimates','yearEstimates','stateEstimates','areaEstimates', 'selectDatabase','limitEdn','limitSector','limitYear','hrsCalendarYr','hrsAcademicYr','hrsHigherEdn')

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        instance = getattr(self, 'instance', None)
        if not instance.pk:
            self.fields['selectDatabase'].widget.attrs={"checked":""}
            self.fields['limitEdn'].widget.attrs={"checked":""}
            self.fields['limitSector'].widget.attrs={"checked":""}
            self.fields['limitYear'].widget.attrs={"checked":"All"}
        self.fields['yearEstimates'].empty_label = None
        self.fields['stateEstimates'].empty_label = None
        self.fields['areaEstimates'].empty_label = None 
        self.helper.layout = Layout(
             HTML("""<p><strong>DEFINE SETUP</strong></p>"""),
             'discountRateEstimates',
             'yearEstimates',
             'stateEstimates',  
             'areaEstimates',   
            Button('EditIndices', 'Option to edit price indices', css_class='btn-primary',onclick="gotofunc();"),
            HTML("""<hr><p><strong>DEFINE PRICE SEARCH</strong></p>"""),
            'selectDatabase',
            HTML("""<br><p>Limit database of prices by the following criteria:</p>"""), 
            Div(
                Row('limitEdn',   css_class='span6'),
                Row('limitSector', css_class='span6'),
                Row('limitYear',   css_class='span6'),
            css_class='row-fluid'),
            HTML("""<hr><p><strong>DEFINE DEFAULT VALUES FOR WAGE CONVERTER</strong></p>"""),
            'hrsCalendarYr',
            'hrsAcademicYr',
            'hrsHigherEdn',
        )

        self.helper.form_tag = False

class GeographicalForm(forms.ModelForm):
    stateIndex = forms.CharField(required=False,label="State")
    areaIndex  = forms.CharField(required=False,label="Area")
    geoIndex = forms.DecimalField(max_digits=6,decimal_places=2,required=False,label="Index")

    class Meta:
        model = GeographicalIndices
        fields = ('stateIndex', 'areaIndex','geoIndex')

    def __init__(self, *args, **kwargs):
        super(GeographicalForm, self).__init__(*args, **kwargs)
        self.queryset = GeographicalIndices.objects.all()

class GeographicalForm_orig(forms.ModelForm):
    stateIndex = forms.CharField(required=False,label="State")
    areaIndex  = forms.CharField(required=False,label="Area")
    geoIndex = forms.DecimalField(max_digits=6,decimal_places=2,required=False,label="Index")

    class Meta:
        model = GeographicalIndices
        fields = ('stateIndex', 'areaIndex','geoIndex')

    def __init__(self, *args, **kwargs):
        super(GeographicalForm_orig, self).__init__(*args, **kwargs)
        self.queryset = GeographicalIndices_orig.objects.all()

class InflationForm(forms.ModelForm):
    yearCPI  = forms.IntegerField(required=False,label="Year")
    indexCPI = forms.DecimalField(max_digits=6,decimal_places=2,required=False,label="CPI")

    class Meta:
        model = InflationIndices
        fields = ('yearCPI','indexCPI')

    def __init__(self, *args, **kwargs):
        super(InflationForm, self).__init__(*args, **kwargs)
        self.queryset = InflationIndices.objects.all()

class InflationForm_orig(forms.ModelForm):
    yearCPI  = forms.IntegerField(required=False,label="Year")
    indexCPI = forms.DecimalField(max_digits=6,decimal_places=2,required=False,label="CPI")

    class Meta:
        model = InflationIndices_orig
        fields = ('yearCPI','indexCPI')

    def __init__(self, *args, **kwargs):
        super(InflationForm_orig, self).__init__(*args, **kwargs)
        self.queryset = InflationIndices_orig.objects.all()

class ProgramsForm(forms.ModelForm):
    progname = forms.CharField(label="Name of the program:",error_messages = {'required': "The Program Name is required"})
    progshortname = forms.CharField(label="Short name:",error_messages = {'required': "The Short Name is required"})

    class Meta:
        model = Programs
        exclude = ['projectId']
        fields = ('progname','progshortname')

class ProgramDescForm(forms.ModelForm):
    progobjective = forms.CharField(required=False, widget=forms.Textarea(), label="Objective of the program:")
    progsubjects = forms.CharField(required=False, widget=forms.Textarea(), label="Subjects / Participants:")
    progdescription = forms.CharField(required=False, widget=forms.Textarea(), label="Brief description:")
    numberofparticipants = forms.DecimalField(max_digits=6,decimal_places=2,min_value=0.01,label="Average number of participants:", error_messages = {'required': "The Average number of participants is required"})
    lengthofprogram = forms.ChoiceField(choices=(('One year or less', 'One year or less'), ('More than one year', 'More than one year')),initial = 'One year or less',label="Length of the program:")
    numberofyears = forms.IntegerField(required=False, label="Number of years ")

    class Meta:
        model = ProgramDesc
        exclude = ['programId']
        fields = ('progobjective','progsubjects','progdescription', 'lengthofprogram', 'numberofyears','numberofparticipants')

    def __init__(self, *args, **kwargs):
        super(ProgramDescForm, self).__init__(*args, **kwargs)
        self.lengthofprogram = 'One year or less' 
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
             Field('progobjective', rows="4", cols="100", css_class='input-xlarge'),
             Field('progsubjects', rows="4", cols="100", css_class='input-xlarge'), 
             Field('progdescription', rows="4", cols="100", css_class='input-xlarge'),
             Div(
                Row('lengthofprogram',   css_class='span6'),
                Row('numberofyears',   css_class='span6'),
            css_class='row-fluid'),
            'numberofparticipants',
        )

        self.helper.form_tag = False
       
class ParticipantsForm(forms.ModelForm):
    yearnumber = forms.IntegerField(required=False, label="Year:")
    noofparticipants = forms.DecimalField(required=False, max_digits=6,decimal_places=2,min_value=0.01,label="Number of participants per year:")

    class Meta:
        model = ParticipantsPerYear
        exclude = ['programId']
        fields = ('yearnumber', 'noofparticipants')

class EffectForm(forms.ModelForm):
    sourceeffectdata = forms.CharField(required=False, widget=forms.Textarea(), label = "Source of effectiveness data:")
    url = forms.URLField(required=False, label = "URL:")
    effectdescription = forms.CharField(required=False, widget=forms.Textarea(), label = "Description of effectiveness data:")
    avgeffectperparticipant = forms.CharField(label = "Average effectiveness per participant:", error_messages = {'required': "The Average Effect Per Participant is required"})
    unitmeasureeffect = forms.CharField(required=False, label = "What is the unit of this measure of effectiveness?")
    sigeffect = forms.ChoiceField(required=False, choices=(('Sig.' ,'Sig.'), ('Not Sig.','Not Sig.')), label = "Is the estimator effect of the treatment statistically significant?")

    class Meta:
        model = Effectiveness
        exclude = ['programId']
        fields = ('sourceeffectdata', 'url', 'effectdescription', 'avgeffectperparticipant','unitmeasureeffect', 'sigeffect') 

    def __init__(self, *args, **kwargs):
        super(EffectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field('sourceeffectdata', rows="4", cols="100", css_class='input-xlarge'),
            'url',
            Field('effectdescription', rows="4", cols="100", css_class='input-xlarge'),
          )
        self.helper.form_tag = False

class PricesForm(forms.ModelForm):
    yrquery = InflationIndices.objects.values_list('yearCPI', flat=True).distinct()
    yrquery_choices =  [(id, id) for id in yrquery]
    iquery = GeographicalIndices.objects.values_list('stateIndex', flat=True).distinct()
    iquery_choices =  [(id, id) for id in iquery]
    areaquery = GeographicalIndices.objects.values_list('areaIndex', flat=True).distinct()
    areaquery_choices =  [(id, id) for id in areaquery]
    choicesPersonnel = (('Hour','Hour'),('Day','Day'),('Week','Week'),('K-12 academic year','K-12 academic year'), ('Higher Ed academic year', 'Higher Ed academic year'),('Calendar year','Calendar year'))
    choicesNonPer = (('Inches','Inches'),('Meters','Meters'),('Sq. Ft.','Sq. Ft.'), ('Sq. Mt.', 'Sq. Mt.'),('Item','Item'))
    category = forms.CharField(required=False,label="Select the category for this ingredient:")
    ingredient  = forms.CharField(required=False,label="Name of the ingredient:")
    edLevel = forms.CharField(required=False,label="Education level to be served:")
    sector = forms.CharField(required=False,label="Sector:")
    descriptionPrice = forms.CharField(required=False,label="Description:")
    unitMeasurePrice = forms.ChoiceField(choicesPersonnel, required=False, widget=forms.Select(),label="Unit of Measure:")
    price = forms.DecimalField(required=False, max_digits=6,decimal_places=2,min_value=0.01,label="Price per unit:")
    yearPrice = forms.ChoiceField(yrquery_choices, required=False, widget=forms.Select(),label="Year of the listed price:")
    statePrice  = forms.ChoiceField(iquery_choices, required=False, widget=forms.Select(), label="To which geographical location does this price correspond to?")
    areaPrice = forms.ChoiceField(areaquery_choices, required=False, widget=forms.Select(), label="")
    sourcePriceData = forms.CharField(required=False,label="Source:")
    urlPrice = forms.URLField(required=False,label="URL:")

    class Meta:
        model = Prices
        fields = ('ingredient','category','edLevel','sector','descriptionPrice','price','unitMeasurePrice','statePrice','areaPrice','yearPrice','sourcePriceData','urlPrice')
