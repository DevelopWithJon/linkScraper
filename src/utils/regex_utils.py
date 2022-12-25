import re

def end_of_url(site, statement):
    
    if site == "realtor.com":
        r = r"\?(.*)"
        return re.match(statement, r)