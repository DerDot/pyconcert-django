from eventowl.models import UserProfile
def user_details(strategy, details, user=None, *args, **kwargs):
    print "City", strategy.session_get('city')
    if kwargs["is_new"]:
        print(kwargs)
        
def create_user_profile(strategy, user, *args, **kwargs):
    city = strategy.session_get('city')
    if city is not None:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.city = city
        profile.save()
        print "Created user profile"