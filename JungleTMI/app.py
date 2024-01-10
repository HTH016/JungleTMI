from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session, redirect
import sys

app = Flask(__name__)
app.secret_key = "JUNGLE"

client = MongoClient('localhost', 27017)
db = client.dbjungle


# API #1: HTML Ʋ(template) ����
@app.route('/')
def main():
    if 'member_id' in session:
        member_id = session['member_id']
        return render_template('hub.html', member_id=member_id)
    else:
        return render_template('login.html')
        #return redirect('/main')


#API #: ȸ������ ������ �ε� 
@app.route('/signup', methods=['GET'])
def sign_up():

    return render_template('signup.html')


#API # : ȸ������ �Է� 
@app.route('/signup', methods=['POST'])
def join_member():
    
    #HTML�κ��� �޴� ���� 
    member_id = request.form['username']
    member_passwd = request.form['password']
    member_name = request.form['fullname']
    print(member_id, member_passwd, member_name)
    
    # �ʱ� ����Ʈ�� ���� ���� ����
    member_point = 1000
    
    # DB member �÷��ǿ� �߰� 
    insert_dict = {'id':member_id, 'password':member_passwd, 'name':member_name, 'point':member_point}
    db.users.insert_one(insert_dict)
    
    #return jsonify({'result': 'success'})
    return redirect('/')

#API # ȸ������ ���̵� �ߺ� �˻�
@app.route('/join/confirm', methods=['POST'])
def join_confirm():
    #���̵� �ߺ�Ȯ�� ��ư Ŭ���� �ϸ� �Է� �ؽ�Ʈ�� �Ѱܹ޴´�.
    confirm_id = request.form['member_id']
    exist = bool(db.users.find_one({'_id', confirm_id}))
    return jsonify({'result':'success', 'exist':exist})

#API # : �α��� 
@app.route('/login', methods=['POST'])
def login():
    
    #HTML�κ��� �޴� ���� 
    login_id = request.form['username']
    login_passwd = request.form['password']
     
    # DB�κ��� ȸ�� ����  
    login_dict = {'id':login_id, 'password':login_passwd}
    result = db.users.find_one(login_dict)
    
    if result is not None:
    #�α��� ����
        session['member_id'] = login_id
        print(session['member_id'], file=sys.stderr)
        print('login_id', session['member_id'], file=sys.stderr)
        return redirect('/main')
        #return render_template('hub.html', member_id=session['member_id'])
        
    #�α��� ���� 
    else:
        return redirect('/')

@app.route('/main')
def hub():
    member_id=session['member_id']
    return render_template('hub.html', member_id=member_id)


#API # : �α׾ƿ�
@app.route('/logout', methods=['GET'])
def logout():
    
    session.pop('member_id', None)
    return redirect('/')


#API #: ���� ������ �ε� 
@app.route('/quizgenerator', methods=['GET'])
def insert_quiz():

    #ȸ�� id�� �޴´�.
    member_id = session['member_id']
    print("���� ������ �ε�", file=sys.stderr)
    return render_template('quizgenerator.html', member_id=member_id)


#API #: ���� ���� ���� 
@app.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    
    member_id = session['member_id']
    
    #HTML�κ��� �޴� ���� 
    quiz_content = request.form['quiz_content']
    quiz_choice_1 = request.form['quiz_choice_1']
    quiz_choice_2 = request.form['quiz_choice_2']
    quiz_choice_3 = request.form['quiz_choice_3']
    quiz_choice_4 = request.form['quiz_choice_4']
    quiz_answer = request.form['quiz_answer']
    
    #���� ��ȣ ����
    quiz_cnt = db.quizzes.count()
    
    # DB member �÷��ǿ� �߰� 
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
    