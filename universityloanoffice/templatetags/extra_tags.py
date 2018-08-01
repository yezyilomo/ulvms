from django import template

register = template.Library()

#A tag for running python codes on templates
@register.simple_tag(name='eval', takes_context=True)
def tg(context, python_expr):
    local_variables=locals()
    for var in context:
        if isinstance(var, dict):
            local_variables.update(var)
    return eval(str(python_expr), local_variables)

@register.filter(name='stw')
def stw(value1):
    return str(value).upper()
