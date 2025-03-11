from flask import Flask,request, url_for, redirect, render_template
import pickle
import numpy as np
import pandas as pd
import mysql.connector as connector
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

model=pickle.load(open('finalized_model.sav','rb'))

@app.route('/')
def home():
    conn = connector.connect(user='root', password='123456', host='localhost', port='3306', database='my_db')
    my_cursor = conn.cursor()
    my_cursor.execute('Select * from price_sentiment')
    result = my_cursor.fetchall()
    data = pd.DataFrame(result, columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock_Splits', 'Score', 'Positive' , 'Negative', 'Neutral', 'Total_Sentiment'])
    data.set_index('Date', drop=True,inplace=True)
    data.drop(['Open', 'High', 'Low', 'Dividends', 'Stock_Splits', 'Score'], inplace=True, axis=1)
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    input_data = data_scaled[-14: ,].reshape(1,14,6)
    prediction = model.predict(input_data)

    arr = [prediction.flatten()[0],  prediction.flatten()[0], prediction.flatten()[0], prediction.flatten()[0], prediction.flatten()[0], prediction.flatten()[0]]

    arr = np.array(arr).reshape(1,-1)

    y_pred_future = scaler.inverse_transform(arr)[0][0]
    ori = data['Close'][-1]
    conn.close()
    my_cursor.close()

    labels = data.index[-14:].tolist()
    values = data['Close'][-14:].tolist()

    values_pos = int(data['Positive'][-14:].sum())
    values_neg = int(data['Negative'][-14:].sum())
    values_neu = int(data['Neutral'][-14:].sum())

    return render_template("app.html", prediction_value = round(y_pred_future,2), original_value = ori, labels_price = labels , values_price = values,
     values_sentiment = [values_pos,values_neg,values_neu])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')