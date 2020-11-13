var http = require('http');
var express = require('express');
var path = require('path');
var static = require('serve-static');
var fs = require('fs');
var url = require('url');
var bodyParser = require('body-parser');
var session = require('express-session');
var mysql = require('mysql2');
var connection;

var app = express();
var router = express.Router();
var port = 50000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended : true}));
app.use(session({
    secret : 'keyboard cat',
    resave : false,
    saveUninitialized : true,
}));
//__dirname는 서버의 루트 주소
app.use('/', static(path.join(__dirname, '/')));
//라우터 만들기
router.post('/create', function(req, res){
    if(req.body.team_leader == '' || req.body.team_0 == '' || req.body.team_1 == '' || req.body.title == '' || req.body.description == '' || req.body.phone_number == ''){
        res.write('<p>You Should Input all blank</p>');
        res.end();
    }
    else{
        //우선 세션에 저장한다.
        req.session.team_leader = req.body.team_leader;
        req.session.team_0 = req.body.team_1;
        req.session.team_1 = req.body.team_0;
        req.session.title = req.body.title;
        req.session.desciption = req.body.description;
        req.session.phone_number = req.body.phone_number;
        insert_data(req.body);
        res.redirect('/');
    }
});
//app이랑 router랑 연결시켜준다.
app.use('/', router);

function insert_data(body){
    sql = {leaderName : body.team_leader, leaderId : 20150326, leaderMail : 'hello@gamil.com', leaderPhone : body.phone_number, title : body.title, description : body.description};
    connection.query('insert into table1 set ? ', sql,  function(err, result, fields){
        if(err){
            console.log(err);
            return;
        }
        console.log('Insert data to table1 complete');
        sql = {memberName : body.team_1, memberId : 20150326, leaderId : 20150327};
        connection.query('insert into table2 set ? ', sql, function(err, result, fields){
            if(err){
                console.log(err);
                return;
            }
            console.log('Insert data to table2 complete');
        })
    });
}


function connect_database(){
    connection = mysql.createConnection({
        host : 'localhost',
        user : 'root',
        password : 'root',
        database : 'my_test_db',
    });
    connection.connect();
    console.log('DataBase Connected!!!!!');
}

function check_table1_exist_make(){
    var sql = 'SHOW TABLES LIKE "table1"';
    connection.query(sql, function(err, result, fields){
        if(err){
            console.log(err);
        }
        //table이 없다는 것
        if(result.length == 0){
            sql = 'CREATE TABLE table1 (' + 'leaderName VARCHAR(32) NOT NULL, leaderId INT PRIMARY KEY AUTO_INCREMENT, leaderMail VARCHAR(32) NOT NULL, leaderPhone VARCHAR(32) NOT NULL, title VARCHAR(32) NOT NULL, ';
            sql += 'description VARCHAR(100) NOT NULL);'
            connection.query(sql, function(err, result, fields){
                if(err){
                    console.log(err);
                }
                console.log('Create Table1!!!');
            })
        }
        //table이 있다는 것
        else{
            console.log('Table1 Already Existed!!');
        }
    })
}

function check_table2_exist_make(){
    var sql = 'SHOW TABLES LIKE "table2"';
    connection.query(sql, function(err, result, fields){
        if(err){
            console.log(err);
        }
        //table이 없다는 것
        if(result.length == 0){
            sql = 'CREATE TABLE table2 (' + 'memberName VARCHAR(32) NOT NULL, memberId INT NOT NULL, leaderId INT NOT NULL, FOREIGN KEY(leaderId) REFERENCES table1(leaderId) ON UPDATE CASCADE);';
            connection.query(sql, function(err, result, fields){
                if(err){
                    console.log(err);
                }
                console.log('Create Table2!!!');
            })
        }
        //table이 있다는 것
        else{
            console.log('Table2 Already Existed!!');
        }
    })
}

var server = http.createServer(app).listen(port, function(){
    console.log(`Web Server Start!!!! listen port : ${port}`);
    connect_database();
    check_table1_exist_make();
    check_table2_exist_make();
});

server.on('request', function(req, res){
    var url_ = req.url;
    //기초 url
    if(url_ == '/'){
        var data = fs.readFileSync('./participation_application.html', 'utf8');
        res.write(data);
        res.end();
    }
})