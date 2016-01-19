from user_agents import parse


def parse_user_agent(request):
    try:
        ua_string = request.META['HTTP_USER_AGENT']
        return parse(ua_string)
    except KeyError:
        return None


def is_robot(request):
    parsed = parse_user_agent(request)
    if parsed is None:
        return False
    else:
        return parsed.is_bot