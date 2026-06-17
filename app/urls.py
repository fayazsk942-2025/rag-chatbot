from django.urls import path
from . import views

urlpatterns = [

    path('',views.landing,name='landing'),

    path('register/',views.register,name='register'),

    path('login/',views.login_view,name='login'),

    path('logout/',views.logout_view,name='logout'),

    path('home/',views.home,name='home'),

    path('profile/',views.profile,name='profile'),

    path('upload/',views.upload_document,name='upload'),

    path('chat/',views.chat_view,name='chat'),

    path('chat/<int:chat_id>/', views.open_chat, name='open_chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path("share-chat/<int:chat_id>/",views.share_chat,name="share_chat"),

    path("shared/<int:chat_id>/",views.shared_chat,name="shared_chat"),
    path('new-chat/',views.new_chat,name='new_chat'),
    path("upload/", views.upload_document, name="upload_document")
]