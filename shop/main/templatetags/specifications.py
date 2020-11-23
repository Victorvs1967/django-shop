from django import template
from django.utils.safestring import mark_safe
from ..models import Smartphone

register = template.Library()

PRODUCT_SPEC = {
    'notebook': {
        'Size': 'size',
        'Display': 'display',
        'Processor': 'processor',
        'Memory': 'memory',
        'Video': 'video',
        'Battery life': 'battery_life'
    },
    'smartphone': {
        'Size': 'size',
        'Display': 'display',
        'Memory': 'memory',
        'Video': 'video',
        'Battery': 'battery',
        'Sd card': 'sd',
        'Sd memory size': 'sd_memory_size',
        'main cam resolution': 'main_cam_resolution',
        'Front cam resolution': 'front_cam_resolution'
    }
}

TABLE_HEAD = '''
            <table class="table">
                <thead class="thead-light">
                <tr>
                    <th scope="col">#</th>
                    <th scope="col">Characteristic name</th>
                    <th scope="col">Value</th>
                </tr>
                </thead>
                <tbody>
            '''
TABLE_TAIL = '''
                </tbody>
            </table>
            '''

def get_product_spec(product, model_name):
    table_content = ''
    i = 0
    for name, value in PRODUCT_SPEC[model_name].items():
        i += 1
        val = getattr(product, value)
        if name == 'Sd card': val = 'Yes' if val else 'No'
        table_content += f'''
                            <tr>
                                <th scope="row">{i}</th>
                                <td>{name}</td>
                                <td>{val}</td>
                            </tr>
                        '''
    return table_content

@register.filter
def product_spec(product):
    model_name = product.get_model_name()
    PRODUCT_SPEC['smartphone']['Sd memory size'] = 'sd_memory_size'
    if isinstance(product, Smartphone):
        if not product.sd:
            PRODUCT_SPEC['smartphone'].pop('Sd memory size')
        else:
            PRODUCT_SPEC['smartphone']['Sd memory size'] = 'sd_memory_size'

    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)
