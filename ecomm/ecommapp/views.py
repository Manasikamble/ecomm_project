from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User 
from django.contrib.auth import login,authenticate,logout
from ecommapp.models import product,cart,orders
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail
# Create your views here.
def about(request):
    return HttpResponse("welcome to django")
def home(request):
    '''context={}
    context['greet']="welcome to DTL"
    context['x']=10
    context['y']=20
    context['l']=[10,20,30,40,50]'''
    print(request.user.is_authenticated)
    return render(request,'home.html')#render redirects to html page
def contactus(request):
    return render(request,'contactus.html')
def index(request):
    p=product.objects.filter(is_active=True)
    context={}
    context['products']=p
    return render(request,'index.html',context) 
def register(request):
    if request.method=='POST':
        uname=request.POST["uname"]
        upass=request.POST["upass"]
        ucpass=request.POST["ucpass"]
        context={}
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="Field cannot be empty"
            return render(request,'register.html',context)
        elif upass!=ucpass:
            context['errmsg']="password and confirm password does not match"
            return render(request,'register.html',context)
        else:
          try:
            u= User.objects.create(password=upass,username=uname,email=uname)
            u.set_password(upass)
            u.save()
            context['success']="User created successfully"
            return render(request,'register.html',context)
          except Exception:
             context['errmsg']="user name already exists"
             return render(request,'register.html',context)
        
    else:
     return render(request,'register.html')
def user_login(request):
    if request.method=='POST':
        uname=request.POST["uname"]
        upass=request.POST["upass"]
        context={}
        if uname==""or upass=="":
           context['errmsg']="Field cannot be empty"
        else:
           u=authenticate(username=uname,password=upass)
           if u is not None:
              login(request,u)  
              return redirect('/index') 
           else:
              context['errmsg']="invalid username and password"
              return render(request,'login.html',context)
    else:       
      return render(request,'login.html')   

def user_logout(request):
       logout(request)
       return redirect('/index') 
def catfilter(request,cv):
   #select*from table where cat=1 and is_active=true
   q1=Q(is_active=True)
   q2=Q(cat=cv)
   p=product.objects.filter(q1 & q2)
   context={}
   context['products']=p
   return render(request,index.html,context)
def sort(request,sv):
   if sv=='0':
      col='price'  #sort by price asc order
   else:
      col='-price'  #sort by price desc order
   p=product.objects.filter(is_active=True).order_by(col)  
   context={}
   context['products']=p
   return render(request,'index.html',context)
def range(request):
   #select*from products where price<=5000 and price>50000 and is_active=true
   min=request.GET['min']
   max=request.GET['max']
   q1=Q(price__gte=min)
   q2=Q(price__lte=max)
   q3=Q(is_active=True)
   p=product.objects.filter(q1 & q2 & q3)
   context={}
   context['products']=p
   return render(request,'index.html',context)
def product_details(request,pid):
   p=product.objects.filter(id=pid)
   print(p)
   context={}
   context['products']=p
   return render(request,'product_details.html',context)
def addtocart(request,pid):
   if request.user.is_authenticated:
      userid=request.user.id
      u=User.objects.filter(id=userid)
      p=product.objects.filter(id=pid)
      q1=Q(uid=u[0])
      q2=Q(pid=p[0])
      c=cart.objects.filter(q1 & q2)
      n=len(c)
      context={}
      context['products']=p
      if n==1:
         context['msg']='product already exixts'
         return render(request,'product_details.html',context)
      else:
       c=cart.objects.create(uid=u[0],pid=p[0])
       c.save()
       context['success']="product added successfully in the cart..."
      return render(request,'product_details.html',context)
   else:
      return redirect('/login')
   
def viewcart(request):
      c=cart.objects.filter(uid=request.user.id)
      s=0
      for x in c:
         s=s+x.pid.price*x.qty
      context={}
      context['data']=c
      context['total']=s
      return render(request,'cart.html',context)
def remove(request,cid):
   c=cart.objects.filter(id=cid)
   c.delete()
   return redirect('/viewcart')
def updateqty(request,qv,cid):
   c=cart.objects.filter(id=cid)
   if qv=='1':
      t=c[0].qty+1
      c.update(qty=t)
   else:
      if c[0].qty>1:
         t=c[0].qty-1
         c.update(qty=t)
      pass
   return redirect('/viewcart') 
def placeorder(request):
   userid=request.user.id
   c=cart.objects.filter(uid=userid)
   oid=random.randrange(1000,9999)
   print("order id is",oid)
   for x in c:
      o=orders.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
      o.save()
      x.delete()
      o1=orders.objects.filter(uid=request.user.id)
      context={}
      context['data']=o1
      np=len(o1)
      s=0
      for x in o1:
         s=s+x.pid.price*x.qty
      context['total'] =s
      context['n']=np  

   return render(request,'placeorder.html',context)
def makepayment(request):
   o1=orders.objects.filter(uid=request.user.id)
   s=0
   np=len(o1)
   for x in o1:
      s=s+x.pid.price*x.qty
      oid=x.order_id
   client = razorpay.Client(auth=("rzp_test_DpxPaCHDgrTo2q", "SsmmXv1qNwqO4asducYqa8ct"))
   data = { "amount": s*100, "currency": "INR", "receipt": "oid" }
   payment = client.order.create(data=data)
   context={}
   context['data']=payment
   return render(request,'pay.html',context)
def sendusermail(request):
   msg="order details are..."
   send_mail(
   "Ekart order placed successfully",
         msg,
         "manasikamble1344@gmail.com",
         ["manasikamble2203@gmail.com"],
         fail_silently=False,  
   )
   return HttpResponse("mail send successfully")


   




       

