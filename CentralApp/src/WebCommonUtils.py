
def get_html_head(title_str = 'FIRST Team 1073 - The Force Team'):
    head_str  = '<head>'
    head_str += '<meta charset="utf-8" />'
    head_str += '<title>%s</title>' % title_str
    head_str += '<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=1, minimum-scale=0.0, maximum-scale=2.0" />'
    head_str += '<link rel="shortcut icon" href="/static/media/images/1073-favicon.ico" type="image/x-icon" />'
    head_str += '<link rel="stylesheet" href="/static/media/css/style.css" type="text/css" media="screen" />'

    head_str += '	<style type="text/css" title="currentStyle">'
    head_str += '		@import "/static/media/css/demo_page.css";'
    head_str += '		@import "/static/media/css/demo_table.css";'
    head_str += '	</style>'

    head_str += '<script type="text/javascript" language="javascript" src="/static/media/js/jquery.js"></script>'
    head_str += '<script type="text/javascript" language="javascript" src="/static/media/js/jquery.dataTables.js"></script>'
    head_str += '</head>'
    
    return head_str
