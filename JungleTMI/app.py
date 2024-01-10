from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session, redirect
import sys

app = Flask(__name__)
app.secret_key = "JUNGLE"

client = MongoClient('localhost', 27017)
db = client.dbjungle


# API #1: HTML 틀(template) 전달
@app.route('/')
def main():
    if 'member_id' in session:
        member_id = session['member_id']
        return render_template('hub.html', member_id=member_id)
    else:
        return render_template('login.html')
        #return redirect('/main')


#API #: 회원가입 페이지 로드 
@app.route('/signup', methods=['GET'])
def sign_up():

    return render_template('signup.html')


#API # : 회원가입 입력 
@app.route('/signup', methods=['POST'])
def join_member():
    
    #HTML로부터 받는 정보 
    member_id = request.form['username']
    member_passwd = request.form['password']
    member_name = request.form['fullname']
    print(member_id, member_passwd, member_name)
    
    # 초기 포인트는 추후 결정 예정
    member_point = 1000
    
    # DB member 컬렉션에 추가 
    insert_dict = {'id':member_id, 'password':member_passwd, 'name':member_name, 'point':member_point}
    db.users.insert_one(insert_dict)
    
    #return jsonify({'result': 'success'})
    return redirect('/')

#API # 회원가입 아이디 중복 검사
@app.route('/join/confirm', methods=['POST'])
def join_confirm():
    #아이디 중복확인 버튼 클릭을 하면 입력 텍스트를 넘겨받는다.
    confirm_id = request.form['member_id']
    exist = bool(db.users.find_one({'_id', confirm_id}))
    return jsonify({'result':'success', 'exist':exist})

#API # : 로그인 
@app.route('/login', methods=['POST'])
def login():
    
    #HTML로부터 받는 정보 
    login_id = request.form['username']
    login_passwd = request.form['password']
     
    # DB로부터 회원 대조  
    login_dict = {'id':login_id, 'password':login_passwd}
    result = db.users.find_one(login_dict)
    
    if result is not None:
    #로그인 성공
        session['member_id'] = login_id
        print(session['member_id'], file=sys.stderr)
        print('login_id', session['member_id'], file=sys.stderr)
        return redirect('/main')
        #return render_template('hub.html', member_id=session['member_id'])
        
    #로그인 실패 
    else:
        return redirect('/')

@app.route('/main')
def hub():
    member_id=session['member_id']
    return render_template('hub.html', member_id=member_id)


#API # : 로그아웃
@app.route('/logout', methods=['GET'])
def logout():
    
    session.pop('member_id', None)
    return redirect('/')


#API #: 출제 페이지 로드 
@app.route('/quizgenerator', methods=['GET'])
def insert_quiz():

    #회원 id를 받는다.
    member_id = session['member_id']
    print("출제 페이지 로드", file=sys.stderr)
    return render_template('quizgenerator.html', member_id=member_id)


#API #: 출제 퀴즈 제출 
@app.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    
    member_id = session['member_id']
    
    #HTML로부터 받는 정보 
    quiz_content = request.form['quiz_content']
    quiz_choice_1 = request.form['quiz_choice_1']
    quiz_choice_2 = request.form['quiz_choice_2']
    quiz_choice_3 = request.form['quiz_choice_3']
    quiz_choice_4 = request.form['quiz_choice_4']
    quiz_answer = request.form['quiz_answer']
    
    #퀴즈 번호 생성
    quiz_cnt = db.quizzes.count()
    
    # DB member 컬렉션에 추가 
    insert_dict = {
        'id': quiz_cnt,
        'submit_id':member_id,
        'problem':quiz_content,
        'option0':quiz_choice_1,
        'option1':quiz_choice_2,
        'option2':quiz_choice_3,
        'option3':quiz_choice_4,
        'answer':quiz_answer
        }
    db.quizzes.insert_one(insert_dict)
    
    #return jsonify({'result': 'success'})
    return render_template('hub.html')
    #return redirect("url") 
    
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    