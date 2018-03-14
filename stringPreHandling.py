# encoding:UTF-8
import re


def delKeyword(target, rules):
    pattern = re.compile(rules)
    matches = pattern.finditer(target)
    for match in matches:
        target = target.replace(match.group(), "")
    return target

# ------------------------------------------------------------------------


def numberTranslator(target):
    rule = ur"[一二两三四五六七八九123456789]万[一二两三四五六七八九123456789](?!(千|百|十))"
    pattern = re.compile(rule)
    matches = pattern.finditer(target)
    text = target
    for match in matches:
        group = match.group()
        gs = group.split(u"万")
        num = 0
        if len(gs) == 2:
            num = num + wordToNumber(gs[0]) * 10000 + \
                wordToNumber(gs[1]) * 1000
        text = text.replace(group, str(num))

    rule = ur"[一二两三四五六七八九123456789]千[一二两三四五六七八九123456789](?!(百|十))"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)
    for match in matches:
        group = match.group()
        gs = group.split(u"千")
        num = 0
        if len(gs) == 2:
            num = num + wordToNumber(gs[0]) * 1000 + wordToNumber(gs[1]) * 100
        text = text.replace(group, str(num))

    rule = ur"[一二两三四五六七八九123456789]百[一二两三四五六七八九123456789](?!十)"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)
    for match in matches:
        group = match.group()
        gs = group.split(u"百")
        num = 0
        if len(gs) == 2:
            num = num + wordToNumber(gs[0]) * 100 + wordToNumber(gs[1]) * 10
        text = text.replace(group, str(num))

    rule = ur"[零一二两三四五六七八九]"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)
    for match in matches:
        group = match.group()
        text = text.replace(group, str(wordToNumber(group)))

    rule = ur"(?<=(周|期))[末天日]"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)
    for match in matches:
        group = match.group()
        text = text.replace(group, str(wordToNumber(group)))

    rule = ur"(?<!(周|期))0?[0-9]?十[0-9]?"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)
    for match in matches:
        group = match.group()
        gs = group.split(u"十")
        num = 0
        if len(gs) == 2:
            if gs[0] == "":
                num += 10
            else:
                ten = int(gs[0])
                num += ten * 10
            if gs[1] != "":
                num += int(gs[1])

            text = text.replace(group, str(num))

    rule = ur"0?[1-9]百[0-9]?[0-9]?"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)
    for match in matches:
        group = match.group()
        gs = group.split(u"百")
        num = 0
        if len(gs) == 2:
            if gs[0] == "":
                num += 100
            else:
                hundred = int(gs[0])
                num += hundred * 100
            if gs[1] != "":
                num += int(gs[1])
            text = text.replace(group, str(num))

    rule = ur"0?[1-9]千[0-9]?[0-9]?[0-9]?"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)

    for match in matches:
        group = match.group()
        gs = group.split(u"千")
        num = 0

        if len(gs) == 2:
            if gs[0] == "":
                num += 1000
            else:
                thousand = int(gs[0])
                num += thousand * 1000
            if gs[1] != "":
                num += int(gs[1])
            text = text.replace(group, str(num))

    rule = ur"[0-9]+万[0-9]?[0-9]?[0-9]?[0-9]?"
    pattern = re.compile(rule)
    matches = pattern.finditer(text)
    for match in matches:
        group = match.group()
        gs = group.split(u"万")
        num = 0
        if len(gs) == 2:
            if gs[0] != "":
                tenthousand = int(gs[0])
                num += tenthousand * 10000
            if gs[1] != "":
                num += int(gs[1])
            text = text.replace(group, str(num))

    return text


# 方法numberTranslator的辅助方法，可将[零-九]正确翻译为[0-9]
# ------------------------------------------------------------------------


def wordToNumber(word):

    if word == u"零" or word == "0":
        return 0
    elif word == u"一" or word == "1":
        return 1
    elif word == u"二" or word == "2" or word == u"两":
        return 2
    elif word == u"三" or word == "3":
        return 3
    elif word == u"四" or word == "4":
        return 4
    elif word == u"五" or word == "5":
        return 5
    elif word == u"六" or word == "6":
        return 6
    elif word == u"七" or word == "7" or word == u"天" or word == u"日" or word == u"末":
        return 7
    elif word == u"八" or word == "8":
        return 8
    elif word == u"九" or word == "9":
        return 9
    else:
        return -1
# ------------------------------------------------------------------------
if __name__ == "__main__":
    test = u"这里有一千两百个人，六百零五个来自中国"

    print numberTranslator(test)
