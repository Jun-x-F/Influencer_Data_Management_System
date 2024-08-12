import bleach

def sanitize_input(input_string):
    return bleach.clean(input_string)



def determine_platform(link):
    if 'youtube.com' in link or 'youtu.be' in link:
        return 'youtube'
    elif 'instagram.com' in link:
        return 'instagram'
    elif 'tiktok.com' in link:
        return 'tiktok'
    else:
        return None
