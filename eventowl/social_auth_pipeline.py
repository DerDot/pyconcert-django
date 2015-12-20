from django.shortcuts import redirect
from social.pipeline.partial import partial

from eventowl.models import UserProfile


def user_details(strategy, details, user=None, *args, **kwargs):
    print(("City", strategy.session_get('city')))
    if kwargs["is_new"]:
        print(kwargs)
        
        
def create_user_profile(strategy, user, *args, **kwargs):
    city = strategy.session_get('city')
    if city is not None:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.city = city
        profile.save()
        print("Created user profile")
        

@partial
def collect_city(strategy, user, backend, *args, **kwargs):
    has_profile = UserProfile.objects.filter(user=user).exists()
    
    if not has_profile:
        city = strategy.session_get('city')
    
        if not city:
            response = redirect('eventowl:account_add_profile')
            params = '?backend={}'.format(backend.name)
            response['Location'] += params
            return response
    
        profile = UserProfile(user=user,
                              city=city)
        profile.save()
        
    return