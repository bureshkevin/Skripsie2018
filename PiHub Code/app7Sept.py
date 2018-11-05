from flask import Flask, render_template, request, redirect, send_file
from sqlite_functions7Sept import lora_sqlite, query_mySQL, close_mySQL
import csv, os, threading
from LoRa8Sept import piLora


app=Flask(__name__)

test=piLora()
lite_db=lora_sqlite()


lora_thread=threading.Thread(target=test.listen)
send_thread=threading.Thread(target=test.testNode)

curDir=os.getcwd()




@app.route('/')
def index():
    print'Initial amount of threads: {}'.format(threading.active_count())
    return render_template('index.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

@app.route('/file', methods=['GET', 'POST'])
def File():

    if request.method == 'POST':
        if request.form['action'] == 'Test Node':
            print'lora close before close thread is {}'.format(threading.active_count())
            test.stop_listen=True
            print'lora close thread is {}'.format(threading.active_count())
            test.stop_send=False
            node=request.form.get('id')
            print'node: {}' .format(node)
            test.stop_listen=False
            return render_template('file.html')
        if request.form['action'] =='Delete':
            lite_db.connect_lite('LoRa')
            lite_db.delete_data()
            return render_template('file.html')
        if request.form['action'] == 'Display Data':
            lite_db.connect_lite('LoRa')
            data=lite_db.pull_data()
            return render_template('file.html', data=data)
        elif request.form['action'] == 'Download CSV':
            lite_db.connect_lite('LoRa')
            data=lite_db.pull_data()
            with open('sqlite/data.csv', 'wb') as data_file:
                writer = csv.writer(data_file, delimiter=',')
                header= ('Data','Device','Date')
                writer.writerow(header)
                for item in data:
                    writer.writerow(item)
            data_file.close()
            data_path=os.path.join(curDir, 'sqlite', 'data'+'.csv')
            return send_file(data_path, attachment_filename='data.csv', as_attachment=True)
        else:
            return render_template('file.html')
    elif request.method=='GET':
        return render_template('file.html')

if __name__ == '__main__':
    lora_thread.start()
    send_thread.start()
    app.run(host='0.0.0.0', threaded=True)
