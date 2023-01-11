import bcrypt
import datetime
from pymongo import MongoClient
from flask import Flask, session, render_template, request, jsonify, escape, redirect, url_for, app
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "helloworld"


client = MongoClient(
    'mongodb+srv://sparta:test@cluster0.280f8z1.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

password = '1234'
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
save_password = hashed_password.decode('utf-8')

@app.route('/')
def home():
    return render_template('index.html')



#회원가입
@app.route("/signup", methods=["POST"]) 
def save_signup():
    id_receive = request.form['id_give']
    pw_receive = bcrypt.hashpw(request.form['pw_give'].encode('utf-8'), bcrypt.gensalt())
    hashed_pw = pw_receive.decode('utf-8')
    mbti_receive = request.form['mbti_give']

    current_id = db.signup.find_one({'id': id_receive}, {'_id': False})

    if current_id == None:
        doc = {
        'id' : id_receive,
        'pw' : hashed_pw,
        'mbti' : mbti_receive
        } 
        db.signup.insert_one(doc)
        
        return jsonify({'msg': '회원가입이 완료되었습니다.'})

    elif id_receive == current_id['id']:
       return jsonify({'msg': '이미 존재하는 아이디 입니다. 아이디 중복체크를 해주세요'})



@app.route("/check", methods=["POST"]) 

def check_id():
    id_receive = request.form['id_give']

    current_id = db.signup.find_one({'id': id_receive}, {'_id': False})

    if current_id == None:
        return jsonify({'msg': '사용 가능한 아이디 입니다.'})
    elif id_receive == current_id['id']:
            return jsonify({'msg': '이미 존재하는 아이디 입니다.'})



# 로그인
@app.route("/login", methods=["POST"])
def login():
    id_receive = request.form['id_give']
    pw_receive = bcrypt.hashpw(
        request.form['pw_give'].encode('utf-8'), bcrypt.gensalt())
    hashed_pw = pw_receive.decode('utf-8') #디코딩해서 db에 꼭 저장

    current_id = db.signup.find_one({'id': id_receive}, {'_id': False})
    current_pw = db.signup.find_one({'id': id_receive}, {'_id': False})
    mbti = db.signup.find_one({'id': id_receive}, {'_id': False})


    a = str(current_pw['pw'])

    current = bcrypt.checkpw(request.form['pw_give'].encode('utf-8'), a.encode('utf-8'))

    if id_receive == current_id['id'] or current_id['id'] == None:
            session['id_give'] = request.form['id_give']   #현정
            session['mbti'] = mbti['mbti']
            return redirect(url_for('index'))
    else:
        return jsonify({'msg': '아이디 또는 비밀번호를 확인해 주세요'})


        
@app.route('/로그인완료')
def index():
    if 'id_give' in session:  # session안에 id_give가 있으면 로그인
        return jsonify({'msg': '어서오세요 %s 님^ㅇ^' %escape(session['id_give'])})
    return render_template('index.html', '글보기.html' '자유게시판.html', '글작성.html',) #세션 보내버리기


@app.route('/logout') #로그아웃
def logout():
    session.clear()
    return redirect(url_for('home'))


#게시판 불러오기
@app.route('/contents', methods=['POST'])
def get_contents():
    cate = request.form['category']
    reversed_close = list(db.articles.find({'category':cate},{'_id':False}))
    all_posting = reversed_close[::-1]
    a = list(range(50))
    return jsonify({'board': all_posting, 'a':a})




@app.route("/page", methods=["POST"])
def a():
    class_cnt = request.form["class_cnt"]
    return redirect(url_for('right',data=class_cnt))


@app.route('/page',  methods=["GET"])
def right(data):
    class_cnt = data
    a = list(db.articles.find({'num':class_cnt},{'_id':False}))
    return jsonify({'next':a})






#게시글 불러오기
@app.route("/content", methods=["POST"])
def content_get():
    uid = request.form['uid']
    created_at = request.form['created_at']
    my_post = db.articles.find_one({'user_id':uid,'created_at':created_at},{'_id':False})
    return my_post

#게시글 보기
@app.route("/detail", methods=["GET"])
def detail():
    return render_template("글보기.html")
#게시판 보기
@app.route("/board")
def board():
    return render_template("자유게시판.html")


@app.route('/like', methods=['POST'])
def like_increase():
    num_receive = request.form['num_give']					# 받아온 name값을 선언
    a = int(num_receive)
    target_post = db.articles.find_one({'num':a})		# like 누른 대상 선언
    target_like = target_post['like']						# 대상의 현재 like수 선언
    target_like_count = target_like + 1					# 현재 like 수 + 1
    db.articles.update_one({'num': a}, {'$set': {'like': target_like_count}}) # 업데이트 진행
    
    return jsonify({'result': 'like', 'msg': '공감했습니다!'})




#공감 수 변경
@app.route('/like', methods=['GET'])
def like_receive():
    num = request.form['num_give']
    target_post = db.articles.find_one({'num':num})
    return target_post

#글 작성
@app.route('/posting', methods=["POST"])
def save_posting():
    title = request.form['editor_title_give']
    content = request.form['content_give']
    category = request.form['category_give']
    now = datetime.datetime.now()
    created_at = str(now.today().isoformat())
    hits = 0
    like = 0
    user_id = session['id_give']
    writer = session['mbti']
    num = len(list(db.articles.find({},{'_id':False})))+1


    doc = {
        'category' : category,
        'title' : title,
        'content' : content,
        'created_at' : created_at,
        'hits' : hits,
        'like' : like,
        'user_id':user_id,
        'writer':writer,
        'num': num,
    }

    db.articles.insert_one(doc)
    return jsonify({'msg': '등록 완료^ㅇ^'})




#댓글저장
@app.route("/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form["comment_give"]
    url = request.form["url"]
    writer = session['mbti']
    now = datetime.datetime.now()
    created_at = str(now.date().isoformat())
 
    doc = {
        'comment':comment_receive,
        'writer':writer,
        'url':url,
        'created_at':created_at
    }

    db.comment.insert_one(doc)  
    return jsonify({'msg':'댓글 작성완료'})   

#댓글불러오기
@app.route("/comment", methods=["GET"])
def comment_get():
    reversed_close = list(db.comment.find({},{'_id':False}))
    comment_list = reversed_close[::-1]
    return jsonify({'comment':comment_list})





#베스트글 조회      
@app.route('/bestPost', methods=["POST"])
def best_post():
    bestpost = db.articles.find_one({'like': -1}, {'_id': False})
    return jsonify({'result': bestpost})







@app.route('/showposting')
def show_posting():
   return render_template('글보기.html')



@app.route('/moyeojo')
def 개발자():
   return render_template('개발자소개.html')
@app.route('/board?category=freeboard')
def 자유게시판():
   return render_template('자유게시판.html')
@app.route('/board?category=bestboard')
def 베스트글():
   return render_template('베스트글.html')  
@app.route('/board?category=loveboard')
def 연애상담소():
   return render_template('연애상담소.html')
@app.route('/board?category=jobboard')
def 취업():
   return render_template('취업Q&A.html')
@app.route('/posting')
def posting():
   return render_template('posting.html')
@app.route('/signup')
def signup():
   return render_template('signup.html')





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


#session['user'] = request.form['id_give']   #현정
        #return render_template('로그인.html')