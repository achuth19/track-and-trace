from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . models import User,entity_list,product,batch,serials,report,startenddates
from . tasks import send_daily_reports_task
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from datetime import datetime
import json
from django.http import JsonResponse
def index(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "emailreport/index.html", {
                "message": "Passwords must match."
            })
        try:
            user= User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "emailreport/index.html", {
                "message": "Username already taken."
            })
        return HttpResponseRedirect(reverse("login"))
    return render(request,'emailreport/index.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user= authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse(entities))
        else:
            return render(request, "emailreport/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "emailreport/login.html")

@login_required
def entities(request):
    if request.method == "POST":
        entity_name=request.POST['entity']
        location=request.POST['location']
        role=request.POST['role']
        user_details=request.user
        entity=entity_list(entity_name=entity_name,location=location,role=role,user_details=user_details)
        entity.save()
        entities=entity_list.objects.filter(user_details=user_details)
        return render(request,"emailreport/choose.html",{"entities":entities})
    return render(request,"emailreport/home.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# def view_entity(request):
#     if request.method=='POST':
#         return render(request,"emailreport/product.html")
#     user=request.user
#     entities=entity_list.objects.filter(user_details=user)
#     return render(request,"emailreport/viewentity.html",{'entities':entities})

@login_required
def producting(request,pk):
    if request.method == "POST":
        user_details=request.user
        product_name=request.POST['product_name']
        email_duration=request.POST['email_duration']
        entity=entity_list.objects.get(pk=pk)
        user_details.is_created_product=True
        user_details.save()
        products=product(product_name=product_name,email_duration=email_duration,linked_entity=entity,user_details=user_details)
        products.save()
        prod=product.objects.filter(linked_entity=entity)
        return render(request,"emailreport/batch.html",{"products":prod,"entity":entity})
    entity=entity_list.objects.get(pk=pk)
    return render(request,"emailreport/product.html",{"entity":entity})

@login_required
def create_batch(request,pk):
    if request.method == "POST":
        batch_name=request.POST['batch_name']
        quantity=int(request.POST['Quantity'])
        product_name=request.POST['product_name']
        products=product.objects.get(product_name=product_name)
        batches=batch(batch_name=batch_name,quantity=quantity,linked_product=products)
        batches.save()
        bat=batch.objects.get(batch_name=batch_name)
        for i in range(quantity):
            serial=serials(linked_product=products,linked_batch=bat,date=datetime.now())
            serial.save()
        return HttpResponse("batch created successfully")
    entity=entity_list.objects.get(pk=pk)
    prod=product.objects.filter(linked_entity=entity)
    return render(request,"emailreport/batch.html",{"products":prod,"entity":entity})

# @login_required
# def next(request):
#     return render(request,"emailreport/next.html")

@login_required
def choose(request):
    if request.method=="POST":
        user_details=request.user
        entity_name=request.POST['entity_value']
        entity=entity_list.objects.get(user_details=user_details,entity_name=entity_name)
        return render(request,"emailreport/product.html",{"entity":entity})
    user=request.user
    entities=entity_list.objects.filter(user_details=user)
    return render(request,"emailreport/choose.html",{'entities':entities})

def unsubscribe(request,email):
    try:
        user = User.objects.get(email=email)
        user.is_subscribed = False
        user.save()
        return render(request, 'emailreport/unsubscribe_confirmation.html')
    except User.DoesNotExist:
        return HttpResponse("you havent subscribed")
    
# def dashboard(request):
#     user=request.user
#     entities=entity_list.objects.filter(user_details=user)
#     locations=[]
#     for entity in entities:
#         locations.append(entity.location)
#     productss=product.objects.filter(user_details=user)
#     if request.method == 'POST':
#         user=request.user
#         entity_name=request.POST['entity']
#         location=request.POST['location']
#         product_name=request.POST['products']
#         try:
#             entity=entity_list.objects.get(entity_name=entity_name,user_details=user,location=location)
#             products=product.objects.get(linked_entity=entity,product_name=product_name)
#             print(products)
#         except entity_list.DoesNotExist:
#             return HttpResponse("Entity not found.")
        
#         except product.DoesNotExist:
#             return HttpResponse('product not found')
        
#         product_details = {
#             'labels': ['Totalserials', 'SerialsCommissioned', 'SerialsPacked', 'SerialsShipped', 'SerialsDecommissioned'],
#             'values': [products.totalserials, products.serialscommissioned, products.serialspacked, products.serialsshipped, products.serialsdecommissioned],
#         }
#         # Serialize the data to JSON
#         product_details_json = json.dumps(product_details)
#         return render(request,'emailreport/dashboard.html',{'data':product_details_json,"entities":entities,"products":productss,"locations":locations})
  
#     return render(request,"emailreport/dashboard.html",{'entities':entities,"locations":locations,"products":productss})

def dashboard(request):
    user=request.user
    entites=entity_list.objects.filter(user_details=user)
    return render(request,"emailreport/dashboard.html",{"entities":entites})

def get_entity_locations(request, entity_id):
    try:
        entity = entity_list.objects.get(pk=entity_id, user_details=request.user)
        locations = entity_list.objects.filter(user_details=request.user, entity_name=entity.entity_name).values_list('location', flat=True).distinct()
        return JsonResponse(list(locations), safe=False)
    except entity_list.DoesNotExist:
        return JsonResponse([], safe=False)

def get_entity_location_products(request, entity_id, location):
    try:
        entity = entity_list.objects.get(pk=entity_id, user_details=request.user, location=location)
        products = product.objects.filter(linked_entity=entity, user_details=request.user).values('id', 'product_name')
        return JsonResponse(list(products), safe=False)
    except entity_list.DoesNotExist:
        return JsonResponse([], safe=False)

def get_product_details(request, product_id):
    try:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        product_obj = product.objects.get(pk=product_id, user_details=request.user)       
        serial_obj=serials.objects.filter(linked_product=product_obj)
        total_serials = serial_obj.filter(created_date__range=(start_date, end_date)).count()
        serials_commissioned=serial_obj.filter(commissioned_date__range=(start_date, end_date),is_commissioned=True).count()
        serials_packed=serial_obj.filter(packed_date__range=(start_date, end_date),is_packed=True).count()
        serials_shipped=serial_obj.filter(shipped_date__range=(start_date, end_date),is_shipped=True).count()
        serials_decommissioned=total_serials-serials_commissioned
        product_details = {
            'product_id':product_id,
            'product_name': product_obj.product_name,
            'total_serials': total_serials,
            'serials_commissioned': serials_commissioned,
            'serials_decommissioned': serials_decommissioned,
            'serials_packed': serials_packed,
            'serials_shipped':serials_shipped,
        }
        return JsonResponse(product_details)
    except product.DoesNotExist:
        return JsonResponse({}, safe=False)

def serials_by_category(request, product_id, category):
    try:
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        product_obj = product.objects.get(pk=product_id, user_details=request.user) 
        serial_obj=serials.objects.filter(linked_product=product_obj)
        if category == "generated":
            total_serials = serial_obj.filter(created_date__range=(start_date, end_date)).values_list('id', flat=True)
            return render(request,'emailreport/display.html',{'serial_numbers':total_serials,"category":category,"product_name":product_obj.product_name})
        if category == "commissioned":
            serials_commissioned=serial_obj.filter(commissioned_date__range=(start_date, end_date),is_commissioned=True).values_list('id',flat=True)
            return render(request,'emailreport/display.html',{'serial_numbers':serials_commissioned,"category":category,"product_name":product_obj.product_name})
        if category == "packed":
            serials_packed=serial_obj.filter(packed_date__range=(start_date, end_date),is_packed=True).values_list('id',flat=True)
            return render(request,'emailreport/display.html',{'serial_numbers':serials_packed,"category":category,"product_name":product_obj.product_name})
        if category == "shipped":
            serials_shipped=serial_obj.filter(shipped_date__range=(start_date, end_date),is_shipped=True).values_list('id',flat=True)
            return render(request,'emailreport/display.html',{'serial_numbers':serials_shipped,"category":category,"product_name":product_obj.product_name})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def email(request):
    if request.method == "POST":
         user_details=request.user
         user_details.is_subscribed=True
         user_details.save()
         report_types = request.POST.getlist('report_type')
         start_date_str = request.GET.get('start_date', '')
         end_date_str = request.GET.get('end_date', '')
         for report_type in report_types:
             if report_type == "daily":
                 try:
                     reports=report.objects.get(user_details=user_details)
                     reports.daily_report=True
                     reports.save()
                 except report.DoesNotExist:
                     reports=report(daily_report=True,user_details=user_details)
                     reports.save()
             if report_type == "weekly":
                try:
                     reports=report.objects.get(user_details=user_details)
                     reports.weekly_report=True
                     reports.save()
                except report.DoesNotExist:
                     reports=report(weekly_report=True,user_details=user_details)
                     reports.save()
             if report_type == "daterange":
                try:
                     reports=report.objects.get(user_details=user_details)
                     reports.date_range_report=True
                     reports.save()
                     if start_date_str!="" and end_date_str!="":
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                        try:
                            dates=startenddates.objects.get(user_details=user_details)
                            dates.start_date=start_date
                            dates.end_date=end_date
                            dates.save()
                        except startenddates.DoesNotExist:
                            dates=startenddates(start_date=start_date,end_date=end_date,user_details=user_details)
                            dates.save()
                except report.DoesNotExist:
                     reports=report(date_range_report=True,user_details=user_details)
                     reports.save()
         return HttpResponse("your preference saved")
               
        