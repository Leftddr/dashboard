from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
import ssw_db
import os
import shutil

global_menu_num = 0
global_page_num = 0
global_content_num = 1
datadb = None
image_base_folder = './static/'

app = Flask(__name__)

#게시글을 보여주기 위한 라우터.
@app.route("/show/<one_title>")
def show_content(one_title):
    html_name = 'show.html'

    contents, comments = datadb.show_content(one_title)
    db_images = datadb.show_image(one_title)
    
    if contents == None:
        return redirect(url_for('main_html'))
    contents = list(contents[0])
    dict_com = {}
    images = []
    
    for image in db_images:
        image = list(image)
        image_str = image[0]
        images.append(image_str[2:len(image_str)])
    
    for com in comments:
        com = list(com)
        list_com = []
        list_com.append(com[1])
        list_com.append(com[4])
        dict_com[com[0]] = list_com
    
    print(images)
    
    return render_template(html_name, title = contents[1], author = contents[0], content = contents[2], date = contents[4],
        comments = dict_com, images = images)

#글을 db에 저장하기 위한 라우터
@app.route("/make_content", methods = ['POST'])
def make_content():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        password = request.form['password']
        content = request.form['content']

        datadb.make_content(author, content, title, password)
        print('DB 저장 완료!!!')

        condition_to_exit = "application/octet-stream"
        for f in request.files.getlist('file[]'):
            if condition_to_exit in str(f):
                break
            if os.path.exists('./static/uploads/' + title) == False:
                os.makedirs('./static/uploads/' + title)
            f.save('./static/uploads/' + title + '/' + secure_filename(f.filename))
            datadb.make_image('uploads/' + title + '/' + secure_filename(f.filename), title)
            print('파일 저장 완료!!!')

        return redirect('/')

@app.route("/make_comment", methods = ['POST'])
def make_comment():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        password = request.form['password']
        comment = request.form['comment']
    
        datadb.make_comment(author, comment, title, password)
        return redirect(url_for('show_content', one_title = title))

#글 작성을 위한 라우터
@app.route("/write")
def write_content():
    html_name = 'form.html'
    return render_template(html_name)

#글 조회를 위한 라우터
@app.route("/search",  methods = ['POST'])
def search_content():
    html_name = 'index.html'
    if request.method == 'POST':
        title = request.form['title']
        contents, _ = datadb.show_content(title)

        if contents == len(contents):
            return render_template(html_name, titles = {}, page_num = global_page_num)
        
        to_send = {}
        contents = list(contents[0])
        send_list = []
        send_list.append(contents[1])
        send_list.append(contents[4])
        to_send[global_content_num] = send_list
        return render_template(html_name, titles = to_send, page_num = global_page_num)

@app.route("/check", methods = ['POST'])
def check_content():
    if request.method == 'POST':
        contents = datadb.only_content(request.form['title'])
        return str(len(contents))

@app.route("/check_password", methods = ['POST'])
def check_password():
    if request.method == 'POST':
        password = request.form['password']
        contents = datadb.only_content(request.form['title'])
        if contents == None:
            return "<html>Page Not Found</html>"
        
        contents = list(contents[0])
        if str(password) == contents[3]:
            return "1"
        else:
            return "0"

def check_password_comment(title, comment, password):
    contents = datadb.only_comment(title, comment)
    if contents == None or len(contents) == 0:
        return "0"
    
    contents = list(contents[0])
    print(contents)
    if str(password) == contents[3]:
        return "1"
    else:
        return "0"

@app.route("/revise", methods = ['POST'])
def revise():
    html_name = 'revise.html'
    if request.method == 'POST':
        title = request.form['title']
        contents = datadb.only_content(title)
    
        if contents == None:
            return render_template(html_name)

        contents = list(contents[0])
        return render_template(html_name, title = contents[1], author = contents[0], content = contents[2])

@app.route("/revise_content", methods = ['POST'])
def revise_content():
    if request.method == 'POST':
        ori_title = request.form['ori_title']
        new_title = request.form['new_title']
        author = request.form['author']
        content = request.form['content']
        
        datadb.update_content(author, content, new_title, ori_title)

        return redirect(url_for('show_content', one_title = new_title))

@app.route("/delete", methods = ['POST'])
def delete():
    if request.method == 'POST':
        title = request.form['title']
        image_paths = datadb.delete_content(title)
    
    #이미지가 있는 경로를 만든다.
    for image_path in image_paths:
        image_path = list(image_path)
        list_image_paths = image_path[0].split('/')
        path = image_base_folder
        for list_image_path in list_image_paths:
            if '.' in list_image_path:
                break
            path += list_image_path + '/'

    print('이미지 폴더 삭제 완료')
    
    return redirect('/')

@app.route("/delete_comment", methods = ['POST'])
def delete_comment():
    if request.method == 'POST':
        password = request.form['password']
        title = request.form['title']
        comment = request.form['comment']

        if check_password_comment(title, comment, password) == "0":
            return '비밀번호가 다릅니다'
        
        print("비밀번호 일치")
        datadb.delete_comment(comment, title)

        return redirect(url_for('show_content', one_title = title))

#가장 처음의 라우터이다.
@app.route("/")
def main_html():
    html_name = './index.html'
    results = datadb.show_page(global_page_num)

    to_send = {}
    for idx, content in enumerate(results):
        content = list(content)
        send_list = []
        send_list.append(content[2])
        send_list.append(content[5])
        to_send[global_content_num + idx] = send_list

    return render_template(html_name, titles = to_send, page_num = global_page_num)

def init_db():
    global datadb
    datadb = ssw_db.sw_db('content_table', 'comment_table', 'image_table')
    datadb.check_table_exists()
    datadb.make_row_num()

if __name__ == '__main__':
    init_db()
    app.run(debug = True, host = '0.0.0.0', port = 50000)