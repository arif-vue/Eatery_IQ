from django.urls import path
from . import views
from .webhooks import stripe_webhook

urlpatterns = [
    path('register/', views.register_user),
    path('login/', views.login),

    path('otp/create/', views.create_otp),
    path('otp/verify/', views.verify_otp),
    
    path('password-reset/request/', views.request_password_reset),
    path('reset/otp-verify/', views.verify_otp_reset),
    path('password-reset/confirm/', views.reset_password),
    path('password-change/', views.change_password),

    path('refresh-token/', views.refresh_token),
    
    path('users/', views.list_users),
    path('profile/', views.user_profile),
    # path('users/<int:user_id>/delete/', views.delete_user),
    # path('delete-account/', views.delete_own_account),
    
    # Onboarding endpoints
    path('onboarding/', views.onboarding_progress),
    path('onboarding/get/', views.get_onboarding_progress),
    path('onboarding/update/', views.onboarding_update),
    
    path('google-login/', views.GoogleLoginView.as_view()),
    
    # Document Management endpoints
    path('documents/', views.document_management),
    path('documents/<int:document_id>/', views.document_detail),
    
    # Subscription endpoints
    path('subscription/', views.subscription_management),
    path('subscription/cancel/', views.subscription_cancel),
    path('subscription/<int:subscription_id>/', views.subscription_detail),
    
    # Stripe Payment endpoints
    path('subscription/stripe/setup/', views.create_stripe_products),
    path('subscription/stripe/checkout/', views.create_checkout_session),
    path('subscription/payment/success/', views.payment_success),
    path('subscription/payment/cancel/', views.payment_cancel),
    path('subscription/webhook/', stripe_webhook),  # Stripe webhook endpoint
    
    # Calendar endpoints
    path('calendar/events/', views.calendar_events),
    path('calendar/events/<int:event_id>/', views.calendar_event_detail),
]
