from django.db import models as m
from django.contrib.auth.models import User
import datetime 

class Projects(m.Model):
    projectname = m.CharField(max_length=256)
    typeanalysis = m.CharField(max_length=256)
    typeofcost = m.CharField(max_length=256) 
    created_at = m.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.projectname

class Settings(m.Model):
    discountRateEstimates = m.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    yearEstimates = m.IntegerField(null=True,blank=True)
    stateEstimates = m.CharField(max_length=2000,null=True, blank=True)
    areaEstimates = m.CharField(max_length=2000,null=True, blank=True)
    selectDatabase = m.TextField(max_length=256,null=True, blank=True)
    limitEdn = m.TextField(max_length=256,null=True, blank=True)
    limitSector = m.TextField(max_length=2000,null=True, blank=True)
    limitYear = m.TextField(max_length=2000,null=True, blank=True)
    hrsCalendarYr = m.IntegerField(null=True,blank=True)
    hrsAcademicYr = m.IntegerField(null=True,blank=True)
    hrsHigherEdn = m.IntegerField(null=True,blank=True)
    projectId = m.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return self.discountRateEstimates

class GeographicalIndices(m.Model):
    stateIndex = m.CharField(max_length=2000,null=True, blank=True)
    areaIndex  = m.CharField(max_length=2000,null=True, blank=True)
    geoIndex = m.CharField(max_length=100,null=True,blank=True)

    def __unicode__(self):
        return self.stateIndex

class GeographicalIndices_orig(m.Model):
    stateIndex = m.CharField(max_length=2000,null=True, blank=True)
    areaIndex  = m.CharField(max_length=2000,null=True, blank=True)
    #geoIndex = m.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    geoIndex = m.CharField(max_length=100,null=True,blank=True)

    def __unicode__(self):
        return self.stateIndex

class InflationIndices(m.Model):
    yearCPI  = m.CharField(max_length=10,null=True, blank=True)
    indexCPI = m.CharField(max_length=10,null=True,blank=True)

    def __unicode__(self):
        return unicode(self.yearCPI)

class InflationIndices_orig(m.Model):
    yearCPI  = m.IntegerField(null=True, blank=True)
    #indexCPI = m.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    indexCPI = m.CharField(max_length=10,null=True,blank=True)

    def __unicode__(self):
        return self.yearCPI

class Benefits(m.Model):
    SectorBenefit = m.CharField(max_length=100,null=True,blank=True)	
    EdLevelBenefit = m.CharField(max_length=100,null=True,blank=True)
    PersonnelBenefit = m.CharField(max_length=256,null=True,blank=True)	
    TypeRateBenefit = m.CharField(max_length=256,null=True,blank=True)	
    YearBenefit = m.CharField(max_length=100,null=True,blank=True)	
    BenefitRate = m.CharField(max_length=100,null=True,blank=True)	
    SourceBenefitData = m.CharField(max_length=100,null=True,blank=True)	
    URLBenefitData = m.CharField(max_length=256,null=True,blank=True)

    def __unicode__(self):
        return self.SectorBenefit

class Programs(m.Model):
    progname = m.CharField(max_length=256)
    progshortname = m.CharField(max_length=256)
    projectId = m.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return self.progname

class ProgramDesc(m.Model):
    progobjective = m.CharField(max_length=2000,null=True, blank=True)
    progsubjects = m.CharField(max_length=2000,null=True, blank=True)
    progdescription = m.CharField(max_length=2000,null=True, blank=True)
    numberofparticipants = m.DecimalField(max_digits=6,decimal_places=2)
    lengthofprogram = m.CharField(max_length=256)
    numberofyears = m.IntegerField(null=True, blank=True)
    programId = m.OneToOneField(Programs, null=True)

    def __unicode__(self):
        return unicode(self.numberofparticipants)

class ParticipantsPerYear(m.Model):
    yearnumber = m.IntegerField(null=True, blank=True)
    noofparticipants = m.DecimalField(max_digits=6,decimal_places=2,null=True, blank=True)
    programdescId = m.ForeignKey(ProgramDesc)

    def __unicode__(self):
        return self.yearnumber 

class Effectiveness(m.Model):
    sourceeffectdata = m.CharField(max_length=2000,null=True, blank=True)
    url = m.CharField(max_length=256,null=True, blank=True)
    effectdescription = m.CharField(max_length=2000,null=True, blank=True)
    avgeffectperparticipant = m.CharField(max_length=256)
    unitmeasureeffect = m.CharField(max_length=2000,null=True, blank=True)
    sigeffect = m.CharField(max_length=10,null=True, blank=True)
    programId = m.OneToOneField(Programs)

    def __unicode__(self):
        return self.sourceeffectdata   

class UserProfile(m.Model):
    user = m.OneToOneField(User)
    organisation = m.CharField(max_length=2000)
    position = m.CharField(max_length=2000)
    licenseSigned = m.CharField(max_length=3)
    signed_at = m.DateField('Date')

    def __unicode__(self):
        return self.user.username

class Prices(m.Model):
    priceProvider = m.CharField(max_length=256,null=True, blank=True)
    category = m.CharField(max_length=256,null=True, blank=True)
    ingredient = m.CharField(max_length=2000,null=True, blank=True)	
    edLevel = m.CharField(max_length=256,null=True, blank=True)	
    sector = m.CharField(max_length=256,null=True, blank=True)
    descriptionPrice = m.CharField(max_length=2000,null=True, blank=True)	
    unitMeasurePrice = m.CharField(max_length=256,null=True, blank=True)	
    price = m.CharField(max_length=100,null=True, blank=True)	
    yearPrice = m.CharField(max_length=100,null=True, blank=True)	
    statePrice = m.CharField(max_length=256,null=True, blank=True)	
    areaPrice = m.CharField(max_length=256,null=True, blank=True)	
    sourcePriceData = m.CharField(max_length=256,null=True, blank=True)	
    urlPrice = m.CharField(max_length=2000,null=True, blank=True)	
    lastChecked = m.CharField(max_length=2000,null=True, blank=True)	
    nextCheckDate = m.CharField(max_length=256,null=True, blank=True)

    def __unicode__(self):
        return unicode(self.priceProvider)

class Ingredients(m.Model):
    category = m.CharField(max_length=256,null=True, blank=True)
    ingredient = m.CharField(max_length=2000,null=True, blank=True)
    edLevel = m.CharField(max_length=256,null=True, blank=True)
    sector = m.CharField(max_length=256,null=True, blank=True)
    unitMeasurePrice = m.CharField(max_length=256,null=True, blank=True)
    price = m.CharField(max_length=100,null=True, blank=True)
    sourcePriceData = m.CharField(max_length=256,null=True, blank=True)
    urlPrice = m.CharField(max_length=2000,null=True, blank=True)
    hrsCalendarYr = m.IntegerField(null=True,blank=True)
    hrsAcademicYr = m.IntegerField(null=True,blank=True)
    hrsHigherEdn = m.IntegerField(null=True,blank=True)
    newMeasure = m.CharField(max_length=256,null=True, blank=True)
    convertedPrice = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    lifetimeAsset = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    interestRate = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    priceAdjAmortization = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    benefitYN = m.CharField(max_length=1,null=True,blank=True)
    benefitRate = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    SourceBenefitData = m.CharField(max_length=100,null=True,blank=True)
    priceAdjBenefits = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    percentageofUsage  = m.IntegerField(null=True,blank=True)
    yearPrice = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    statePrice = m.CharField(max_length=2000,null=True, blank=True)
    areaPrice = m.CharField(max_length=2000,null=True, blank=True)
    geoIndex = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    indexCPI = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    yearQtyUsed = m.IntegerField(null=True,blank=True)
    quantityUsed = m.IntegerField(null=True,blank=True)
    variableFixed = m.CharField(max_length=10,null=True,blank=True)
    priceAdjInflation = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    priceAdjGeographicalArea = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    priceNetPresentValue = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    adjPricePerIngredient = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    costPerIngredient = m.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    programId = m.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return self.ingredient

