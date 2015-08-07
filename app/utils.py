import bbcode
import re

def check_input(input):
    whitelist = ['abs','sin','cos','tan']
    if re.search('[\?_">\\<=\'{}\[\]]',input):
        raise Exception("Unwanted symbols")

    for word in re.findall('[a-zA-Z]+',input):
        if word not in whitelist:
            raise Exception("Unallowed word: %s" % word)

def bb_to_html(bbtext):
    parser = bbcode.Parser()
    parser.newline = '<br>'
    def input_formatter(tag_name, value, options, parent, context):
        tag ='<input type="'+options['type']
        if 'name' in options:
            tag+='" name="'+options['name']
        if 'value' in options:
            tag+='" value="'+options['value']

        return '<input type="%s" name="%s" value="%s" >' %(options['type'],options['name'],options['value'])
    
            
    parser.add_formatter('input',input_formatter,standalone = True)
    return parser.format(bbtext)
