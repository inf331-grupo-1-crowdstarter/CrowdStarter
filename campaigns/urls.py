from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("registro/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("protegido/", views.protected_view, name="protected"),
]
urlpatterns += [
    path("campanas/", views.campaign_list, name="campaign_list"),
    path("campanas/<int:pk>/", views.campaign_detail, name="campaign_detail"),
]

urlpatterns += [
    path("campanas/crear/", views.campaign_create, name="campaign_create"),
    path("campanas/<int:pk>/publicar/", views.campaign_publish, name="campaign_publish"),
]

urlpatterns += [path("campanas/<int:pk>/editar/", views.campaign_edit, name="campaign_edit")]

urlpatterns += [path("campanas/<int:pk>/eliminar/", views.campaign_delete, name="campaign_delete")]

urlpatterns += [path("campanas/<int:pk>/aportar/", views.campaign_contribute, name="campaign_contribute")]

urlpatterns += [
    path("campanas/<int:pk>/comentarios/", views.comment_create, name="comment_create"),
    path("campanas/<int:pk>/comentarios/<int:comment_pk>/eliminar/", views.comment_delete, name="comment_delete"),
]

urlpatterns += [path("campanas/panel_del_creador/", views.creator_panel, name="creator_panel")]
urlpatterns += [path("mis-aportes/", views.user_contribution_history, name="user_history_contributions")]