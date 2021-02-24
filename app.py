from flask import Flask, render_template, request, redirect, url_for
from ML import PredictDisease
import json
import socket
import dns
from pymongo import MongoClient

mn_r = "mongodb+srv://therealrahulsahu:rahulsahu1_@democluster.2u6fb.gcp.mongodb.net/check_my_disease?retryWrites=true&w=majority"
mn_y = "mongodb+srv://user12:w9jTSFswVHlOToRm@cluster0.fjcc4.mongodb.net/check_my_disease?retryWrites=true&w=majority"
myclient = MongoClient(mn_y)
DB = myclient["check_my_disease"]

hostname = socket.gethostname()
ip_addr = socket.gethostbyname(hostname)

app = Flask(__name__)
data_model = PredictDisease()

app.my_ip = ip_addr
app.my_port = 80


def getLinks(dname):
    table = DB["remedies"]
    my_row = table.find_one({"name": dname})
    return my_row

def deleteUser(username):
    table = DB['user']
    table.delete_many({"username": username})

def addUser(username, password):
    table = DB['user']
    table.insert_one({"username": username, "password": password})

def checkForUser(username, password):
    table = DB["user"]
    rows = table.find({"username": username})
    try:
        single = rows[0]
        if single["password"] == password:
            return True
        else:
            return False
    except IndexError:
        return False


@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        add_user(username, password)
        result = {'status': 'success'}
        return json.dumps(result)

@app.route('/user_login', methods=['POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result_set = {}
        if len(username) == 0 or len(password) == 0:
            valid = False
        else:
            valid = checkForUser(username, password)
        result_set['valid'] = valid
        return json.dumps(result_set)



@app.route('/predict/<location>', methods=['POST'])
def predict(location):
    if request.method == 'POST':
        if location == 'first_list':
            return json.dumps({'result': data_model.get_disease_list()})
        if location == 'first_iter':
            d_name = request.form['d_name']
            if len(d_name) == 0:
                return json.dumps({'final': -1})
            else:
                return json.dumps(data_model.predict(d_name))
        if location == 'second_iter':
            node = request.form['node']
            decision = request.form['decision']
            if decision == 'true':
                decision = 1
            elif decision == 'false':
                decision = 0
            return json.dumps(data_model.recurse_predict(node, decision))
        if location == 'final_result':
            node = request.form['node']
            d_list = json.loads(request.form['d_list'])

            rt_data = data_model.final_result(node, d_list)
            links = getLinks(rt_data["disease"])
            try:
                rt_data["about"] = links["about"]
            except:
                rt_data["about"] = "https://www.mayoclinic.org/"
            try:
                rt_data["treatment"] = links["treatment"]
            except:
                rt_data["treatment"] = "https://www.mayoclinic.org/"
            try:
                rt_data["doctor"] = links["doctor"]
            except:
                rt_data["doctor"] = "https://www.justdial.com/Indore/57/Doctor_fil"

            #print(rt_data)
            return json.dumps(rt_data)


@app.route('/')
def root():
    return redirect(url_for('home'))


@app.route('/disease_p')
def disease_p():
    return render_template('disease_p.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/dep')
def dep():
    return render_template('dep.html')


@app.route('/doctor')
def doctor():
    return render_template('doctor.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/single_blog')
def single_blog():
    return render_template('single-blog.html')



if __name__ == '__main__':
    app.run(host=app.my_ip, port=app.my_port)
