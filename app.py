from flask import Flask, redirect, render_template, url_for, request, flash, session, escape
from dbhelper import getUserInfo, createNewUser, createNewUrl, getAllUrlsByAuthor, authUser, isUserExist, getLongUrlByShort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very-secret-key'

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return redirect('/users/{}'.format(session['username']))

    return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registr.html')
    elif request.method == 'POST':
        login = request.form['login'].replace(' ', '')
        password = request.form['password'].replace(' ', '')
        repeatPassword = request.form['repeat-password'].replace(' ', '')

        if not login or not password or not repeatPassword:
            flash('Заполните все поля для продолжения!')
            return redirect('/registration')
        
        if password != repeatPassword:
            flash('Пароли не совпадают, проверьте правильность ввода')
            return redirect('/registration')

        result = createNewUser(login, password)

        if result:
            session['username'] = login
            return redirect('/users/{}'.format(login))
        else:
            flash('Такой пользователь уже существует!')
            return redirect('/registration')

@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'GET':
        return render_template('auth.html')
    elif request.method == 'POST':
        login = request.form['login'].replace(' ', '')
        password = request.form['password'].replace(' ', '')

        if not login or not password:
            flash('Заполните все поля для продолжения!')
            return redirect('/authorization')
        
        result = authUser(login, password)

        if result:
            session['username'] = login
            return redirect('/users/{}'.format(login))
        else:
            flash('Логин или пароль не совпадают!')
            return redirect('/authorization')

@app.route('/users/<string:user>', methods=['GET', 'POST'])
def users(user):
    if 'username' in session:
        if session['username'] == user:
            return render_template('userpage.html', user = { 'username': user, 'data': getUserInfo(user) })

    if not isUserExist(user):
        return render_template('userpage.html')

    return render_template('userpage.html', user = { 'username': user })

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/cutter', methods=['GET', 'POST'])
def cutter():
    if 'username' in session:
        if request.method == 'POST':
            longUrl = request.form['longUrl']
            shortUrl = request.form['shortUrl']

            if not longUrl:
                flash('Длинная ссылка не должна быть пустым полем!')
                return redirect('/cutter')

            result = createNewUrl(longUrl, shortUrl, session['username'])

            if result:
                flash('Сокращённая ссылка была добавлена!')
                return redirect('/cutter')
            else: 
                flash('Не удалось добавить ссылку!')
                return redirect('/cutter')
    else:
        flash('Чтобы сокращать ссылки, нужно авторизоваться!')
    
    return render_template('cutter.html')

@app.route('/url/<string:url>')
def urlRedirecter(url):
    path = getLongUrlByShort(url)
    return redirect(path)

if __name__ == '__main__':
    app.run()