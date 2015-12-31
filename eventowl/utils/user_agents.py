from user_agents import parse


def parse_user_agent(request):
    ua_string = request.META['HTTP_USER_AGENT']
    return parse(ua_string)
    

def is_robot(request):
    parsed = parse_user_agent(request)
    return parsed.is_bot