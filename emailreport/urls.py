from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views
urlpatterns=[
    path("",views.index,name="index"),
    path('login',views.login_view,name="login"),
    path('entities',views.entities,name="entities"),
    # path('view_entity',views.view_entity,name="view_entity"),
    path('product/<int:pk>',views.producting,name="product"),
    path('logout',views.logout_view,name="logout"),
    path('batch/<int:pk>',views.create_batch,name="batch"),
    # path('continue',views.next,name="continue"),
    path('choose',views.choose,name="choose"),
    path('unsubscribe/<str:email>',views.unsubscribe,name="unsubscribe"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('get_entity_locations/<int:entity_id>/', views.get_entity_locations, name='get_entity_locations'),
    path('get_entity_location_products/<int:entity_id>/<str:location>/', views.get_entity_location_products, name='get_entity_location_products'),
    path('get_product_details/<int:product_id>/', views.get_product_details, name='get_product_details'),
    path('serials_by_category/<int:product_id>/<str:category>/', views.serials_by_category, name='serials_by_category'),
    path('email',views.email,name="email")
]