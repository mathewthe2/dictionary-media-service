import re

CURRICULUMS = {
   'JLPT': ["N" + str(n+1) for n in range(5)],
   'WK':["WK" + str(n+1) for n in range(60)]
}

def get_level(entry, curriculum):
    tags = entry[7].split(' ')
    for tag in tags:
        if tag in CURRICULUMS[curriculum]:
            return int(re.findall('\d+', tag)[0])
    return None

def word_is_within_difficulty(user_levels, entry):
    # JLPT, N1 is highest
    # WK, WK60 is highest
    jlpt_level = get_level(entry, 'JLPT')
    skip_jlpt_filter = jlpt_level is None or user_levels['JLPT'] is None
    is_within_jlpt = True if skip_jlpt_filter else user_levels['JLPT'] <= jlpt_level
    
    wk_level = get_level(entry, 'WK')
    skip_wk_filter = wk_level is None or user_levels['WK'] is None
    is_within_wk = True if skip_wk_filter else user_levels['WK'] >= wk_level
    if (skip_jlpt_filter and skip_wk_filter):
        return True
    elif skip_jlpt_filter and not skip_wk_filter:
        return is_within_wk
    elif skip_wk_filter and not skip_jlpt_filter:
        return is_within_jlpt
    else:
        return is_within_jlpt or is_within_wk