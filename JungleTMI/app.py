from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, session, redirect
from datetime import date
import sys
import os

UPLOAD_FOLDER = '/static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

SUBMIT_LIMIT = 20 # 하루에 출제할 수 있는 문제 한도
CARD_PROBLEM_DISP_MAX = 20 # 카드에 표시되는 문제의 최대 길이; 더 길면 생략됨

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/static/images'
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
app.secret_key = "JUNGLE" # 세션 비밀 키

client = MongoClient('mongodb://test:test@13.209.42.99', 27017)
db = client.dbjungle



# API #1: HTML 틀(template) 전달
@app.route('/')
def main():
    if 'member_id' in session:
        member_id = session['member_id']

        # 사용자명 세션에서 추출
        user = db.users.find_one({'id':member_id})
        user_name = user['name']
        user_point = user['point']

        # DB에서 리더보드 추출하는 함수
        # first_place = {'name':'테스터', 'point':1500}
        # second_place = {'name':'테스터2', 'point':1200}
        # third_place = {'name':'테스터3', 'point':1000}
        leaderboard = getLeaderBoard()

        return render_template('hub.html', user_name=user_name, user_point=user_point, first_place=leaderboard[0], second_place=leaderboard[1], third_place=leaderboard[2])
    else:
        return render_template('login.html')


#API #: 회원가입 페이지 로드 
@app.route('/signup', methods=['GET'])
def sign_up():

    return render_template('signup.html')

#API # : 회원가입 입력 
@app.route('/signup', methods=['POST'])
def join_member():
    cur_date = date.today().strftime("%y%m%d") # 현재 날짜 생성
    
    #HTML로부터 받는 정보 
    print("파일 결과", request.files, file=sys.stderr)
    member_id = request.form['username']
    member_passwd = request.form['password']
    member_name = request.form['fullname']
    #member_image = request.form['img']
    
    #이미지 저장
    currentPath = os.getcwd()
    f = request.files['img']
    print("Received img file")
    print(f,file=sys.stderr)
    file_dir = '/static/images/'+ secure_filename(f.filename)
    
    if (secure_filename(f.filename) == ""):
        abs_file_dir = currentPath + '/static/images/default_profile.jpg'
        file_dir = '/static/images/default_profile.jpg'
    else:
        abs_file_dir = currentPath + file_dir
        f.save(abs_file_dir)

    # 초기 포인트는 추후 결정 예정
    member_point = 0
    
    # DB member 컬렉션에 추가 
    insert_dict = {'id':member_id, 'password':member_passwd, 'name':member_name, 'point':member_point, 'img_src':file_dir, 'join_date':cur_date}
    db.users.insert_one(insert_dict)
    
    
    #return 'done!'
    #return jsonify({'result': 'success'})
    return redirect('/')


# #API # : 회원가입 입력 
# @app.route('/signup', methods=['POST'])
# def join_member():
#     cur_date = date.today().strftime("%y%m%d") # 현재 날짜 생성
    
#     #HTML로부터 받는 정보 
#     member_id = request.form['username']
#     member_passwd = request.form['password']
#     member_name = request.form['fullname']
#     # print(member_id, member_passwd, member_name)
    
#     # 초기 포인트는 추후 결정 예정
#     member_point = 0
    
#     # DB member 컬렉션에 추가 
#     insert_dict = {'id':member_id, 'password':member_passwd, 'name':member_name, 'point':member_point, 'join_date':cur_date}
#     db.users.insert_one(insert_dict)
    
#     #return jsonify({'result': 'success'})
#     return redirect('/')


# #API # 회원가입 아이디 중복 검사
@app.route('/idconfirm', methods=['POST'])
def join_confirm():
    #아이디 중복확인 버튼 클릭을 하면 입력 텍스트를 넘겨받는다.
    confirm_id = request.form['member_id']
    print(confirm_id, file=sys.stderr)
    exist = bool(db.users.find_one({'id': confirm_id}))
    print(exist, file=sys.stderr)
    if exist == True:
    #중복
        #새 창 띄우기
        return jsonify({'id_taken': 'yes'})
    else :
    #중복아님    
        return jsonify({'id_taken': 'no'})



#API # 회원가입 아이디 중복 검사
# @app.route('/join/confirm', methods=['POST'])
# def join_confirm():
#     #아이디 중복확인 버튼 클릭을 하면 입력 텍스트를 넘겨받는다.
#     confirm_id = request.form['member_id']
#     exist = bool(db.users.find_one({'_id', confirm_id}))
#     return jsonify({'result':'success', 'exist':exist})


#API # : 로그인
@app.route('/login', methods=['POST'])
def login():
    
    # #HTML로부터 받는 정보 
    login_id = request.form['username']
    login_passwd = request.form['password']
     
    # # DB로부터 회원 대조  
    # login_dict = {'id':login_id, 'password':login_passwd}
    # result = db.users.find_one(login_dict)
    
    # if result is not None:
    # #로그인 성공
    #     session['member_id'] = login_id
    #     print(session['member_id'], file=sys.stderr)
    #     print('login_id', session['member_id'], file=sys.stderr)
    #     return redirect('/')
    #     #return render_template('hub.html', member_id=session['member_id'])
        
    # #로그인 실패 
    # else:
    #     return redirect('/')
    
    # DB로부터 회원 대조  
    user = db.users.find_one({'id':login_id})
    
    if user is not None:
        user = db.users.find_one({'id':login_id, 'password':login_passwd})
        if user is not None:
            #로그인 성공
            session['member_id'] = login_id
            print(session['member_id'], file=sys.stderr)
            print('login_id', session['member_id'], file=sys.stderr)
            # return redirect('/')
            #return render_template('hub.html', member_id=session['member_id'])
            return jsonify({'result':'success', 'reason':''})
        else:
            # 로그인 실패; 패스워드 불일치
            return jsonify({'result':'fail', 'reason':'wrong_password'})
    else:
        #로그인 실패; 아이디 없음
        return jsonify({'result':'fail', 'reason':'no_id'})


#API # : 로그아웃
@app.route('/logout', methods=['GET'])
def logout():
    
    session.pop('member_id', None)
    return redirect('/')


# @app.route('/main')
# def hub():
#     member_id=session['member_id']
#     return render_template('hub.html', member_id=member_id)


#API #: 출제 페이지 로드 
@app.route('/quizgenerator', methods=['GET'])
def insert_quiz():

    #회원 id를 받는다.
    member_id = session['member_id']
    print("출제 페이지 로드", file=sys.stderr)
    return render_template('quizgenerator.html', member_id=member_id)


#API #: 출제 퀴즈 제출 
@app.route('/quizsubmit', methods=['POST'])
def submit_quiz():
    
    member_id = session['member_id']
    user = db.users.find_one({'id':member_id})
    cur_date = date.today().strftime("%y%m%d") # 출제 한도 체크를 위해 현재 날짜 생성

    today_quiz_count = db.quizzes.count_documents({'submit_id':member_id, 'submit_date':cur_date})
    if today_quiz_count >= SUBMIT_LIMIT:
        # 출제 한도 초과; 실패 정보 전송
        return jsonify({'result': 'fail', 'reason':'over_limit'})
    
    #HTML로부터 받는 정보 
    quiz_content = request.form['quiz_content']
    quiz_choice_1 = request.form['quiz_choice_1']
    quiz_choice_2 = request.form['quiz_choice_2']
    quiz_choice_3 = request.form['quiz_choice_3']
    quiz_choice_4 = request.form['quiz_choice_4']
    quiz_answer = int(request.form['option'])
    
    #퀴즈 번호 생성
    quiz_cnt = db.quizzes.count_documents({})
    
    # DB member 컬렉션에 추가 
    insert_dict = {
        'id': quiz_cnt,
        'submit_id':member_id,
        'problem':quiz_content,
        'option0':quiz_choice_1,
        'option1':quiz_choice_2,
        'option2':quiz_choice_3,
        'option3':quiz_choice_4,
        'answer':quiz_answer,
        'submit_date':cur_date # 출제 한도 체크를 위해 날짜 저장
        }
    db.quizzes.insert_one(insert_dict)

    # 100 포인트 지급
    new_point = user['point'] + 100
    db.users.update_one({'id':user['id']}, {'$set': {'point':new_point}})

    # return jsonify({'result': 'success'})
    # return render_template('hub.html')
    # return redirect("/")

    # 출제 성공; 성공 정보 전송
    return jsonify({'result': 'success', 'reason':''})


# 새 문제 리스트
@app.route('/list')
def newQuizList():
    member_id = session['member_id']
    user = db.users.find_one({'id':member_id})

    # user = db.users.find_one({}) # 임시 유저 객체
    
    quiz_list = getNewQuizList(user)

    if len(quiz_list) == 0:
        # 풀 퀴즈가 하나도 없는 경우
        no_quiz_to_show = True
    else:
        no_quiz_to_show = False

    # quiz_list = [ # 임시 퀴즈 리스트
    #     {'id': 1, 'submit_name': '테스터', 'correct_ratio':11}
    # ]
    
    # print(quiz_list)
    

    return render_template('quizList.html', quiz_list=quiz_list, no_quiz_to_show=no_quiz_to_show)
    # return render_template('quizList.html', quiz_list=quiz_list, no_quiz_to_show= (len(quiz_list) == 0) )


# 푼 문제 리스트
@app.route('/list/solved')
def solvedQuizList():
    member_id = session['member_id']
    user = db.users.find_one({'id':member_id})

    quiz_list = getSolvedQuizList(user)

    if len(quiz_list) == 0:
        # 푼 퀴즈가 하나도 없는 경우
        no_quiz_to_show = True
    else:
        no_quiz_to_show = False

    return render_template('quizListSolved.html', quiz_list=quiz_list, no_quiz_to_show=no_quiz_to_show)


# 출제한 문제 리스트
@app.route('/list/my')
def myQuizList():
    member_id = session['member_id']
    user = db.users.find_one({'id':member_id})

    quiz_list = getMyQuizList(user)

    if len(quiz_list) == 0:
        # 풀 퀴즈가 하나도 없는 경우
        no_quiz_to_show = True
    else:
        no_quiz_to_show = False

    # quiz_list = [ # 임시 퀴즈 리스트
    #     {'id': 1, 'submit_name': '테스터', 'correct_ratio':11}
    # ]
    
    # print(quiz_list)
    

    return render_template('quizListMy.html', quiz_list=quiz_list, no_quiz_to_show=no_quiz_to_show)
    # return render_template('quizList.html', quiz_list=quiz_list, no_quiz_to_show= (len(quiz_list) == 0) )


# 퀴즈 페이지 표시
@app.route('/quiz', methods=['POST'])
def showQuiz():
    quiz_id = int(request.form['quiz_id'])
    quiz = db.quizzes.find_one({'id':quiz_id})
    if quiz is None:
        # 해당 ID를 가진 퀴즈가 없는 경우 에러
        print("ERROR, no matching quiz for id " + quiz_id)
    

    submit_user = db.users.find_one({'id':quiz['submit_id']})
    if submit_user is None:
        # 해당 ID를 가진 출제자가 없는 경우 에러
        print("ERROR, no matching user for id " + quiz['submit_id'])
    else:
        submit_name = submit_user['name']

    return render_template('quiz.html', quiz=quiz, submit_name=submit_name)


# 정답 맞추기
@app.route('/api/solve', methods=['POST'])
def checkAnswer():
    quiz_id = int(request.form['quiz_id'])
    cur_date = date.today().strftime("%y%m%d") # 현재 날짜

    # 퀴즈 ID로부터 퀴즈 정답 추출
    quiz = db.quizzes.find_one({'id': quiz_id})

    correct_idx = quiz['answer']
    correct_ans = getCorrectAnswer(quiz)

    member_id = session['member_id']
    user = db.users.find_one({'id':member_id})
    # user = db.users.find_one({}) # 임시 유저 객체
    user_id = user['id']




    ans = int(request.form['option'])
    # 정답 확인
    if ans == correct_idx:
        # 정답
        new_point = user['point'] + 500 # 정답 시 500포인트 추가
        db.users.update_one({'id':user_id}, {'$set': {'point':new_point}})

        # 기록DB에 항목 추가
        new_record = {'quiz_id':quiz_id, 'solver_id':user_id,'is_correct':1, 'solve_date':cur_date}
        db.records.insert_one(new_record)

        return jsonify({'result': 'correct', 'correct_ans': correct_ans})
    else:
        # 오답
        # 기록DB에 항목 추가
        new_record = {'quiz_id':quiz_id, 'solver_id':user_id,'is_correct':0, 'solve_date':cur_date}
        db.records.insert_one(new_record)

        return jsonify({'result': 'incorrect', 'correct_ans': correct_ans})











# # HTML 화면 보여주기 
# @app.route('/')
# def home():
#     member_id=session['member_id']
    
#     user = db.users.find_one({'id':member_id})
#     user_name = user['name']
#     # first_place = {'name':'테스터', 'point':1500}
#     # second_place = {'name':'테스터2', 'point':1200}
#     # third_place = {'name':'테스터3', 'point':1000}
#     leaderboard = getLeaderBoard()
#     return render_template('hub.html', user_name=user_name, first_place=leaderboard[0], second_place=leaderboard[1], third_place=leaderboard[2])


# @app.route('/list')
# def quizList():
#     user = db.users.find_one({}) # 임시 유저 객체
#     quiz_list = getQuizList(user)

#     if len(quiz_list) == 0:
#         # 풀 퀴즈가 하나도 없는 경우
#         no_quiz_to_show = True
#     else:
#         no_quiz_to_show = False

#     # quiz_list = [ # 임시 퀴즈 리스트
#     #     {'id': 1, 'submit_name': '테스터', 'correct_ratio':11}
#     # ]
    
#     # print(quiz_list)
    

#     return render_template('quizList.html', quiz_list=quiz_list, no_quiz_to_show=no_quiz_to_show)
#     # return render_template('quizList.html', quiz_list=quiz_list, no_quiz_to_show= (len(quiz_list) == 0) )


# @app.route('/quiz', methods=['POST'])
# def showQuiz():


#     # member_id = session['member_id']

#     quiz_id = int(request.form['quiz_id'])
#     quiz = db.quizzes.find_one({'id':quiz_id})
#     if quiz is None:
#         # 해당 ID를 가진 퀴즈가 없는 경우 에러
#         print("ERROR, no matching quiz for id " + quiz_id)
    

#     submit_user = db.users.find_one({'id':quiz['submit_id']})
#     if submit_user is None:
#         # 해당 ID를 가진 출제자가 없는 경우 에러
#         print("ERROR, no matching user for id " + quiz['submit_id'])
#     else:
#         submit_name = submit_user['name']

#     return render_template('old_quizSolve.html', quiz=quiz, submit_name=submit_name)


# @app.route('/api/solve', methods=['POST'])
# def checkAnswer():
#     quiz_id = int(request.form['quiz_id'])

#     # 퀴즈 ID로부터 퀴즈 정답 추출
#     quiz = db.quizzes.find_one({'id': quiz_id})

#     correct_idx = quiz['answer']
#     correct_ans = getCorrectAnswer(quiz)

#     user = db.users.find_one({}) # 임시 유저 객체
#     user_id = user['id']




#     ans = int(request.form['option'])
#     # 정답 확인
#     if ans == correct_idx:
#         # 정답
#         new_point = user['point'] + 500 # 정답 시 500포인트 추가
#         db.users.update_one({'id':user_id}, {'$set': {'point':new_point}})

#         # 기록DB에 항목 추가
#         new_record = {'quiz_id':quiz_id, 'solver_id':user_id,'is_correct':1}
#         db.records.insert_one(new_record)

#         return jsonify({'result': 'correct', 'correct_ans': correct_ans})
#     else:
#         # 오답
#         # 기록DB에 항목 추가
#         new_record = {'quiz_id':quiz_id, 'solver_id':user_id,'is_correct':0}
#         db.records.insert_one(new_record)

#         return jsonify({'result': 'incorrect', 'correct_ans': correct_ans})



def getCorrectAnswer(quiz):
    # 퀴즈 객체를 전달받아 정답 char 출력
    ans_idx = quiz['answer']
    if int(ans_idx) == 0:
        return quiz['option0']
    elif int(ans_idx) == 1:
        return quiz['option1']
    elif int(ans_idx) == 2:
        return quiz['option2']
    elif int(ans_idx) == 3:
        return quiz['option3']
    else:
        print("ERROR: invalid ans_idx")


def getCorrectRatio(record_list):
    # 퀴즈 리스트를 받아 정답률을 계산

    if len(record_list) == 0:
        # 아무도 풀지 않음; 정답률 -으로 설정
        correct_ratio = "-"
    else:
        # 해당 퀴즈의 기록을 사용해 정답률 계산
        correct_num = 0
        for record in record_list:
            if record['is_correct']:
                correct_num += 1

        correct_ratio = float(correct_num) / len(record_list) * 100
        correct_ratio = round(correct_ratio)
    
    return correct_ratio
    

def getNewQuizList(user):
    # 해당 유저에게 표시될 새 퀴즈 리스트를 생성
    # 내가 출제하지 않은, 아직 풀지않은 문제만 
    # 퀴즈 리스트 형식은 [id, 출제자 프로필 사진, 출제자 이름, 출제자 id, 문제, 정답, 정답률, 자신 정답 여부]
    quiz_list = []

    all_list = db.quizzes.find({})

    for quiz in all_list:
        if user['id'] == quiz['submit_id']:
            # 해당 유저가 출제자일 경우 스킵
            continue
        
        temp_record = db.records.find_one({'quiz_id':quiz['id'], 'solver_id':user['id']})
        if not(temp_record is None):
            # 해당 유저가 이미 풀었을 경우 스킵
            continue
        
        problem = cutProblem(quiz['problem'])

        # 정답률 계산
        quiz_record_list = list(db.records.find({'quiz_id':quiz['id']}))
        correct_ratio = getCorrectRatio(quiz_record_list)
        
        submit_user = db.users.find_one({'id':quiz['submit_id']})
        if submit_user is None:
            # 해당 ID를 가진 출제자가 없는 경우 에러
            print("ERROR, no matching user for id " + quiz['submit_id'])
        else:
            img_src = submit_user['img_src']
            submit_name = submit_user['name']
            submit_id = submit_user['id']

        temp_quiz = {'id':quiz['id'], 'img_src':img_src, 'submit_name':submit_name, 'submit_id':submit_id, 'problem':problem, 'correct_answer':"N/A", 'correct_ratio':correct_ratio, 'is_correct':0}
        quiz_list.append(temp_quiz)
    
    return quiz_list


def getSolvedQuizList(user):
    # 해당 유저에게 표시될 푼 퀴즈 리스트를 생성
    # 이미 푼 퀴즈의 정답과 정답률, 자신의 정답 여부를 표시
    # 퀴즈 리스트 형식은 [id, 출제자 프로필 사진, 출제자 이름, 출제자 id, 문제, 정답, 정답률, 자신 정답 여부]
    quiz_list = []

    record_list = list(db.records.find({'solver_id':user['id']}))

    for record in record_list:
        # 자신이 푼 기록DB에서 퀴즈를 추출
        quiz_id = record['quiz_id']
        quiz = db.quizzes.find_one({'id':quiz_id})
        submit_user = db.users.find_one({'id':quiz['submit_id']})
        img_src = submit_user['img_src']
        submit_name = submit_user['name']
        submit_id = submit_user['id']
        problem = cutProblem(quiz['problem'])
        correct_answer = getCorrectAnswer(quiz)
        quiz_record_list = list(db.records.find({'quiz_id':quiz['id']}))
        correct_ratio = getCorrectRatio(quiz_record_list)
        is_correct = record['is_correct']

        temp_quiz = {'id':quiz_id, 'img_src':img_src, 'submit_name':submit_name, 'submit_id':submit_id, 'problem':problem, 'correct_answer':correct_answer, 'correct_ratio':correct_ratio, 'is_correct':is_correct}
        quiz_list.append(temp_quiz)
    
    return quiz_list


def getMyQuizList(user):
    # 해당 유저가 출제한 퀴즈 리스트를 생성
    # 출제한 퀴즈의 정답과 정답률을 표시
    # 퀴즈 리스트 형식은 [id, 출제자 프로필 사진, 출제자 이름, 출제자 id, 문제, 정답, 정답률, 자신 정답 여부]
    quiz_list = []

    user_quiz_list = db.quizzes.find({'submit_id':user['id']})

    for quiz in user_quiz_list:
        # 자신이 출제한 퀴즈DB에서 추출
        # 정답률 계산
        quiz_record_list = list(db.records.find({'quiz_id':quiz['id']}))
        correct_ratio = getCorrectRatio(quiz_record_list)
        
        img_src = user['img_src']
        submit_name = user['name']
        submit_id = user['id']

        problem = cutProblem(quiz['problem'])
        correct_answer = getCorrectAnswer(quiz)

        temp_quiz = {'id':quiz['id'], 'img_src':img_src, 'submit_name':submit_name, 'submit_id':submit_id, 'problem':problem, 'correct_answer':correct_answer, 'correct_ratio':correct_ratio, 'is_correct':0}
        quiz_list.append(temp_quiz)
    
    return quiz_list


def cutProblem(problem):
    # 목록 카드에 표시될 문제 길이가 너무 긴 경우 잘라내기
    if len(problem) > CARD_PROBLEM_DISP_MAX:
        prob_out = problem[0:CARD_PROBLEM_DISP_MAX-1] + "..."
    else:
        prob_out = problem
    
    return prob_out


def getLeaderBoard():
    user_list = list(db.users.find().sort("point", -1))
    
    # leaderboard = [
    #     {'name':'NONAME', 'point':0},
    #     {'name':'NONAME', 'point':0},
    #     {'name':'NONAME', 'point':0},
    # ]

    # 빈 리더보드 제작
    leaderboard = [
        {'name':'NONAME', 'point':0} for i in range(3)
    ]

    for i in range( min(3, len(user_list)) ):
        # 사용자 수가 3명 이상이라면 3명을 선택
        # 3명 이하라면 해당 명수 만큼만
        user = user_list[i]
        leaderboard[i]['img_src'] = user['img_src']
        leaderboard[i]['name'] = user['name']
        leaderboard[i]['id'] = user['id']
        leaderboard[i]['point'] = user['point']
    
    return leaderboard




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)