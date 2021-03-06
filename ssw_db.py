import pymysql
from datetime import datetime

class sw_db():

    def __init__(self, content_table, comment_table, image_table):
        self.conn = pymysql.connect(host = 'localhost', user = 'root', password = 'root',
            db = 'sw_db', charset = 'utf8')
        self.cursor = self.conn.cursor()
        #table 이름 저장
        self.content_table = content_table
        self.comment_table = comment_table
        self.image_table = image_table
        print('Connection Complete!!')
    
    def check_table_exists(self):
        sql = "show tables like '%s'" % (self.content_table)
        print(sql)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        if len(res) == 0:
            sql = 'CREATE TABLE '+ (self.content_table)
            sql += '(author varchar(20) not null, title varchar(30) not null PRIMARY KEY, content varchar(200) not null, pw varchar(20) not null,'
            sql += 'date DATETIME not null)'
            print(sql)
            self.cursor.execute(sql)
            self.cursor.fetchall()
            print('content_table 생성 완료')

        sql = "show tables like '%s'" % (self.comment_table)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        if len(res) == 0:
            sql = 'CREATE TABLE ' + (self.comment_table)
            sql += '(author varchar(20) not null, comment varchar(200) not null, title varchar(30) not null, pw varchar(20) not null, date DATETIME not null,'
            sql += 'FOREIGN KEY(title) REFERENCES ' + self.content_table + '(title) ON UPDATE CASCADE)'
            self.cursor.execute(sql)
            self.cursor.fetchall()
            print('comment_table 생성 완료')

        sql = "show tables like '%s'" % (self.image_table)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        if len(res) == 0:
            sql = 'CREATE TABLE ' + (self.image_table)
            sql += '(image_path varchar(100) not null, title varchar(30) not null, date DATETIME not null,'
            sql += 'FOREIGN KEY(title) REFERENCES ' + self.content_table + '(title) ON UPDATE CASCADE)'
            self.cursor.execute(sql)
            self.cursor.fetchall()
            print('image_table 생성 완료')
        
        self.conn.commit()
        print('table complete!!!!')
    
    def make_content(self, author, content, title, password):
        sql = 'INSERT INTO ' + (self.content_table)
        sql += ' VALUES ( "%s", "%s", "%s", "%s", "%s");' % (author, title, content, password, str(datetime.today().strftime("%Y%m%d%H%M%S")))
        print(sql)
        self.cursor.execute(sql)
        self.cursor.fetchall()
        self.conn.commit()
        print('작성 완료!!!')

    def make_comment(self, author, comment, title, password):
        sql = 'INSERT INTO ' + (self.comment_table)
        sql += ' VALUES ( "%s", "%s", "%s", "%s", "%s");' % (author, comment, title, password, str(datetime.today().strftime("%Y%m%d%H%M%S")))
        self.cursor.execute(sql)
        self.cursor.fetchall()
        self.conn.commit()
        print('작성 완료!!!')
    
    def make_image(self, image_path, title):
        sql = 'INSERT INTO ' + (self.image_table)
        sql += ' VALUES ( "%s", "%s", "%s");' % (image_path, title, str(datetime.today().strftime("%Y%m%d%H%M%S")))
        self.cursor.execute(sql)
        self.cursor.fetchall()
        self.conn.commit()
        print('image upload 완료!!')
    
    def make_row_num(self):
        sql = 'set @rownum = 0'
        self.cursor.execute(sql)
        self.cursor.fetchall()
        print('row_num set 0 completed')

        sql = 'select @rownum:=@rownum + 1, A.* '
        sql += 'from(select * from ' + self.content_table + ' ORDER BY date)'
        sql += 'A, (SELECT @rownum:=0) R;'
        self.cursor.execute(sql)
        self.cursor.fetchall()
        self.conn.commit()
        print('row_num 생성 완료!!!')
    
    def show_page(self, page_num):
        sql = 'SELECT * FROM(SELECT @rownum:=@rownum + 1 rnum, A.* FROM content_table A, (SELECT @rownum:=0)r where 1=1) list where rnum >= ' + str(page_num) + ' and rnum <= '
        sql += str(page_num + 10)
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        print('row_num 쿼리 완료!!!')

        return result
    
    def show_content(self, title):
        sql = 'SELECT * FROM ' + self.content_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()

        sql = 'SELECT * FROM ' + self.comment_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        res2 = self.cursor.fetchall()

        return res1, res2

    def only_content(self, title):
        sql = 'SELECT * FROM ' + self.content_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        res1 = self.cursor.fetchall()
        return res1

    def only_comment(self, title, comment):
        sql = 'SELECT * FROM ' + self.comment_table + " WHERE title = '%s' AND comment = '%s'" % (title, comment)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res
    
    def show_image(self, title):
        sql = 'SELECT * FROM ' + self.image_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        res = self.cursor.fetchall()

        return res
    
    def delete_content(self, title):
        sql = 'DELETE FROM ' + self.comment_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        self.cursor.fetchall()

        #이미지는 폴더까지 삭제를 해줘야 하기 때문에 경로를 return 한다.
        sql = 'SELECT * FROM ' + self.image_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        retval = self.cursor.fetchall()

        sql = 'DELETE FROM ' + self.image_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        self.cursor.fetchall()

        sql = 'DELETE FROM ' + self.content_table + " WHERE title = '%s'" % title
        self.cursor.execute(sql)
        self.cursor.fetchall()

        self.conn.commit()

        return retval

    def update_content(self, author, content, new_title, origin_title):
        sql = 'UPDATE ' + self.content_table + ' SET author = "%s", content = "%s", title = "%s", date = "%s" WHERE title = "%s"' \
            %(author, content, new_title, str(datetime.today().strftime("%Y%m%d%H%M%S")), origin_title)

        self.cursor.execute(sql)
        self.cursor.fetchall()
        self.conn.commit()
        print('업데이트 완료!!!')
    
    def delete_comment(self, comment, title):
        new_comment = "삭제된 답글입니다."
        sql = 'UPDATE ' + self.comment_table + ' SET comment = "%s", date = "%s" WHERE title = "%s" AND comment = "%s"' % (new_comment, str(datetime.today().strftime("%Y%m%d%H%M%S")), title, comment)

        self.cursor.execute(sql)
        self.conn.commit()
        print('댓글 삭제 완료')


