'''
Created on Jan 1, 2014

@author: ken_sthilaire
'''
import web
from web import utils

class pureform(web.form.Form):         
    def render(self):
        out= ''
        out+= '<fieldset>\n'
        for i in self.inputs:
            html = utils.safeunicode(i.pre) + i.render() + self.rendernote(i.note) + utils.safeunicode(i.post)
            out += '<div class="pure-control-group" id="%s_div">\n' % (i.id.rstrip(':'))
            out += '    <label for="%s">%s</label>\n' % (i.id, i.id)
            out += '    %s</div>\n' % (html)
        out+= '</fieldset>\n'
        return out