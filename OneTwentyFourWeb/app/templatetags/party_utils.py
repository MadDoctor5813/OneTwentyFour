from django import template

register = template.Library()

party_classes = { 'LIB' : 'info-lib',
                  'PC' : 'info-pc',
                  'NDP' : 'info-ndp',
                  'OTH' : 'info-oth'}

party_names = { 'LIB' : 'Liberal',
                'PC' : 'PC',
                'NDP' : 'NDP',
                'OTH' : 'Other' }

def get_party_class(value):
    return party_classes[value]

def get_party_name(value):
    print(value)
    return party_names[value]

def lookup(value, key):
    return value.get(key, None)

register.filter('party_class', get_party_class),
register.filter('party_name', get_party_name)
register.filter('lookup', lookup)