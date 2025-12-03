import stripe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Subscription
from django.contrib.auth import get_user_model

User = get_user_model()

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook endpoint to handle payment events
    """
    if request.method == "POST":
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        if not endpoint_secret:
            return JsonResponse({
                'success': False,
                'message': 'Webhook secret not configured'
            }, status=500)

        # Verify the webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': 'Invalid payload'
            }, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({
                'success': False,
                'message': 'Invalid signature'
            }, status=400)

        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_checkout_session_completed(session)
            return JsonResponse({
                'success': True,
                'message': 'Checkout session completed successfully'
            }, status=200)

        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            handle_payment_intent_succeeded(payment_intent)
            return JsonResponse({
                'success': True,
                'message': 'Payment succeeded'
            }, status=200)

        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            handle_payment_intent_failed(payment_intent)
            return JsonResponse({
                'success': True,
                'message': 'Payment failed event handled'
            }, status=200)

        # Handle other event types as necessary
        return JsonResponse({
            'success': True,
            'message': f'Event type {event["type"]} received but not handled'
        }, status=200)

    return JsonResponse({
        'success': False,
        'message': 'Only POST requests are allowed'
    }, status=405)


def handle_checkout_session_completed(session):
    """
    Handle successful checkout session completion
    """
    try:
        # Get user ID and subscription plan from metadata
        user_id = session.get('client_reference_id')
        subscription_plan = session.get('metadata', {}).get('plan')

        if not user_id or not subscription_plan:
            print(f"Missing user_id or plan in session metadata")
            return

        # Update subscription status
        try:
            subscription = Subscription.objects.get(user_id=user_id)
            subscription.status = 'active'
            subscription.stripe_session_id = session.get('id')
            subscription.stripe_payment_intent = session.get('payment_intent')
            subscription.save()
            
            print(f"Subscription updated for user {user_id}: {subscription_plan}")

        except Subscription.DoesNotExist:
            print(f"Subscription not found for user {user_id}")

    except Exception as e:
        print(f"Error in handle_checkout_session_completed: {str(e)}")


def handle_payment_intent_succeeded(payment_intent):
    """
    Handle successful payment
    """
    try:
        # Get metadata from payment intent
        metadata = payment_intent.get('metadata', {})
        user_id = metadata.get('user_id')
        
        if user_id:
            try:
                subscription = Subscription.objects.get(user_id=user_id)
                subscription.status = 'active'
                subscription.save()
                print(f"Payment succeeded for user {user_id}")
            except Subscription.DoesNotExist:
                print(f"Subscription not found for user {user_id}")

    except Exception as e:
        print(f"Error in handle_payment_intent_succeeded: {str(e)}")


def handle_payment_intent_failed(payment_intent):
    """
    Handle failed payment
    """
    try:
        # Get metadata from payment intent
        metadata = payment_intent.get('metadata', {})
        user_id = metadata.get('user_id')
        
        if user_id:
            try:
                subscription = Subscription.objects.get(user_id=user_id)
                subscription.status = 'expired'
                subscription.save()
                print(f"Payment failed for user {user_id}")
            except Subscription.DoesNotExist:
                print(f"Subscription not found for user {user_id}")

    except Exception as e:
        print(f"Error in handle_payment_intent_failed: {str(e)}")
