from flask import Flask, render_template, flash, request, session, send_file, jsonify
from flask import render_template, redirect, url_for, request
import mysql.connector
import pickle

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from requests import get
from bs4 import BeautifulSoup
import math
app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaa'

english_bot = ChatBot('Bot',
                      storage_adapter='chatterbot.storage.SQLStorageAdapter',
                      logic_adapters=[
                          {
                              'import_path': 'chatterbot.logic.BestMatch'
                          },

                      ],
                      trainer='chatterbot.trainers.ListTrainer')
english_bot.set_trainer(ListTrainer)
model = pickle.load (open ('Model/model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/Chat')
def Chat():
    return render_template('chat.html')


@app.route('/Predict')
def Predict():
    return render_template('NewQueryReg.html')


@app.route("/ask", methods=['GET', 'POST'])
def ask():
    message = str(request.form['messageText'])

    print('User' + message)
    bot_response = english_bot.get_response(message)

    print(bot_response)

    print(bot_response.confidence)

    while True:

        if bot_response.confidence > 0.4:
            bot_response = str(bot_response)
            print(bot_response)
            return jsonify({'status': 'OK', 'answer': bot_response})


        elif message == ("bye") or message == ("exit"):

            bot_response = 'Hope to see you soon' + '<a href="http://127.0.0.1:5000">Exit</a>'

            print(bot_response)
            return jsonify({'status': 'OK', 'answer': bot_response})

            break



        else:

            try:
                url = "https://en.wikipedia.org/wiki/" + message
                page = get(url).text
                soup = BeautifulSoup(page, "html.parser")
                p = soup.find_all("p")
                return jsonify({'status': 'OK', 'answer': p[1].text})



            except IndexError as error:

                bot_response = 'Sorry i have no idea about that.'

                print(bot_response)
                return jsonify({'status': 'OK', 'answer': bot_response})

    # return render_template("index.html")




@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        city_names = {'0': 'Ahmedabad', '1': 'Bengaluru', '2': 'Chennai', '3': 'Coimbatore', '4': 'Delhi',
                      '5': 'Ghaziabad', '6': 'Hyderabad', '7': 'Indore', '8': 'Jaipur', '9': 'Kanpur', '10': 'Kochi',
                      '11': 'Kolkata', '12': 'Kozhikode', '13': 'Lucknow', '14': 'Mumbai', '15': 'Nagpur',
                      '16': 'Patna', '17': 'Pune', '18': 'Surat'}

        crimes_names = {'0': 'Crime Committed by Juveniles', '1': 'Crime against SC', '2': 'Crime against ST',
                        '3': 'Crime against Senior Citizen', '4': 'Crime against children', '5': 'Crime against women',
                        '6': 'Cyber Crimes', '7': 'Economic Offences', '8': 'Kidnapping', '9': 'Murder'}

        population = {'0': 63.50, '1': 85.00, '2': 87.00, '3': 21.50, '4': 163.10, '5': 23.60, '6': 77.50, '7': 21.70,
                      '8': 30.70, '9': 29.20, '10': 21.20, '11': 141.10, '12': 20.30, '13': 29.00, '14': 184.10,
                      '15': 25.00, '16': 20.50, '17': 50.50, '18': 45.80}

        city_code = request.form["city"]
        crime_code = request.form['crime']
        year = request.form['year']
        pop = population[city_code]

        # Here increasing / decreasing the population as per the year.
        # Assuming that the population growth rate is 1% per year.
        year_diff = int(year) - 2011;
        pop = pop + 0.01 * year_diff * pop

        crime_rate = model.predict([[year, city_code, pop, crime_code]])[0]

        city_name = city_names[city_code]

        crime_type = crimes_names[crime_code]

        if crime_rate <= 1:
            crime_status = "Very Low Crime Area"
        elif crime_rate <= 5:
            crime_status = "Low Crime Area"
        elif crime_rate <= 15:
            crime_status = "High Crime Area"
        else:
            crime_status = "Very High Crime Area"

        cases = math.ceil(crime_rate * pop)

        return render_template('result.html', city_name=city_name, crime_type=crime_type, year=year,
                               crime_status=crime_status, crime_rate=crime_rate, cases=cases, population=pop)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
