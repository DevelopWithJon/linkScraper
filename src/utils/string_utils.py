"""string utils."""

def format_cities(domain, city_list):
    """Format city list to domain specific URL specifications."""
    if domain == "realtor.com":
        return _realtor_city_format(city_list)
    elif domain == "loopnet.com":
        return _loopnet_city_format(city_list)
        

def _realtor_city_format(city_list):
    """format city list for realtor.com."""

    formatted_city_list = []
    try:
        for city in city_list:
            city, state = city.split(",")
            city = city.split()
            if len(city)>1:
                city = "-".join(city)
            else:
                city = city[0]
            formatted_city = city + "_" + state.strip()
            formatted_city_list.append(formatted_city)
            
    except ValueError as e:
        print(e)
    return formatted_city_list

def _loopnet_city_format(city_list):
    """format city list for loopnet.com."""

    formatted_city_list = []
    try:
        for city in city_list:
            city, state = city.split(",")
            city = city.split()
            if len(city)>1:
                city = "-".join(city)
            else:
                city = city[0]
            formatted_city = city + "-" + state.strip()
            formatted_city_list.append(formatted_city)
    except ValueError as e:
        print(e)
    return formatted_city_list