import os
import json
import jinja2
import webapp2
# import datetime
# from google.appengine.api import modules
from models.search_model import search_model

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

ASCII_a = 97
ASCII_z = 122


class Home(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENV.get_template('templates/index.html')
        # self.response.write(template.render(template_values))
        self.response.write(template.render())


class LoadNDB(webapp2.RequestHandler):
    def get(self):
        result = search_model.load_ndb()
        self.response.write(result)


class Search(webapp2.RequestHandler):
    def get(self):

        self.response.headers["Access-Control-Allow-Origin"] = "*"

        tray = ''
        if self.request.get('tray'):
            tray = self.request.get('tray')
        wild_count = 0
        if self.request.get('wc'):
            wild_count = int(self.request.get('wc'))

        return_type = 'html'
        if self.request.get('rt'):
            return_type = self.request.get('rt')  # html or json

        search_mode = 'files'
        # 		if self.request.get('sm'):
        # 			search_mode = self.request.get('sm')

        letter_counts_arr = [0] * 26
        letters_len = 0
        tray_validated = ''

        for i in range(len(tray)):
            charval = ord(tray[i])
            if charval >= ASCII_a and charval <= ASCII_z:
                letter_counts_arr[charval - ASCII_a] += 1
                letters_len += 1
                tray_validated += tray[i]

        for i in range(wild_count):
            tray_validated += '?'

        letters_len += wild_count

        if letters_len < 2:
            self.response.write('Format: pywordfinder.appspot.com/?tray=test&wc=[0+]&rt=[html,json]')
            return

        m = search_model()
        if wild_count == 0:
            results = m.find_words(letters_len, letter_counts_arr, search_mode, return_type)
        else:
            results = m.find_words_wild(letters_len, letter_counts_arr, wild_count, search_mode, return_type)

        if return_type == 'json':
            self.response.headers['Content-Type'] = "application/json"
            self.response.write(json.dumps(results.list_words_list, separators=(',', ':')))
            return

        self.response.headers['Content-Type'] = "text/html; charset=UTF-8"

        # 		version_id = self.request.environ["CURRENT_VERSION_ID"].split('.')[1]
        # 		timestamp = long(version_id) / pow(2,28)
        # 		version = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m/%y %X")

        # template = JINJA_ENV.get_template('templates/results_ajax.html')
        footer = '<p id="results_footer">' + os.environ['SERVER_SOFTWARE'] + '<br />' + results.footer_str + '</p>'
        self.response.write(
            '<h5 id="resultsFor">Results for <span>' + tray_validated + '</span></h5>' + results.result_str + footer)


# 		self.response.write(template.render({
# 			'list_words_list': results.list_words_list,
# 			'total_compares': results.total_compares,
# 			'total_found': results.total_found,
# 			'total_time': results.total_time
# 		}))

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/loadndb', LoadNDB),
    ('/search', Search),
], debug=False)
