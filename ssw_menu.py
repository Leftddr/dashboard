from flask import Flask, render_template
import ssw_db

global_menu_num = 0
global_page_num = 0
global_content_num = 1
datadb = None

app = Flask(__name__)
#라우터이다.
@app.route("/show/<one_title>")
def show_content(one_title):
    print(one_title)

@app.route("/")
def main_html():
    html_name = './main.html'
    results = datadb.show_page(global_page_num)

    to_send = {}
    for idx, content in enumerate(results):
        content = list(content)
        to_send[global_content_num + idx] = content[1]

    return render_template(html_name, titles = to_send, page_num = global_page_num)

def init_db():
    global datadb
    datadb = ssw_db.sw_db('content_table', 'comment_table')
    datadb.check_table_exists()
    datadb.make_row_num()

if __name__ == '__main__':
    init_db()
    app.run(debug = True, host = '0.0.0.0', port = 50000)