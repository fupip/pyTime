# -*- coding: utf-8 -*-
def Enum(**enums):
    return type('Enum', (), enums)

RangeTime = Enum(day_break=3, early_morning=8, morning=10,
                 noon=12, afternoon=15, night=18, latenight=20, midnight=23)
