from flask import Flask, render_template, request, redirect, send_file
from sqlite_functions11Sept import lora_sqlite, query_mySQL
import csv, os, threading
from LoRa11Sept import piLora


app=Flask(__name__)

test=piLora()
lite_db=lora_sqlite()


lora_thread=threading.Thread(target=test.listen)
my_thread=threading.Thread(target=test.mySqlUpload)

curDir=os.getcwd()




@app.route('/')
def index():
    print'Initial amount of threads: {}'.format(threading.active_count())
    return render_template('index.html')

@app.route('/setup', methods=['Get', 'POST'])
def setup():

    if request.method == 'POST':
        if request.form['action'] == 'Add Node':
            test.node=int(request.form.get('id'))
            test.designa=request.form.get('designa')
            test.descrip=request.form.get('descrip')

            print'id: {} disgnation: {} description: {}' .format(test.node, test.designa, test.descrip)
            lite_db.connect_lite('lora')
            print'connected'
            lite_db.update_device_lite(test.designa, test.descrip, test.node)
            print 'uploaded'
            lite_db.close_lite()
            print 'closed'
            test.updateNodes=True
        elif request.form['action'] =='Delete Local Data':
            lite_db.connect_lite('lora')
            lite_db.delete_data()
        elif request.form['action'] == 'mySQL upload':
            test.updateMy=True
            print'button clicked'
    else:
        pass
    return render_template('setup.html')

@app.route('/file', methods=['GET', 'POST'])
def File():

    if request.method == 'POST':
        if request.form['action'] == 'Test Node':
            print'lora close before close thread is {}'.format(threading.active_count())
            print'lora close thread is {}'.format(threading.active_count())
            test.stop_send=False
            test.node=int(request.form.get('id'))
            test.msg=int(request.form.get('msg'))
            print'node: {}' .format(test.node)
            return render_template('file.html')
        elif request.form['action'] == 'Display Data':
            lite_db.connect_lite('lora')
            data=lite_db.pull_data()
            return render_template('file.html', data=data)

        elif request.form['action'] == 'Download Devices':
            lite_db.connect_lite('lora')
            data=lite_db.pull_devices(False)
            with open('sqlite/devices.csv', 'wb') as data_file:
                writer = csv.writer(data_file, delimiter=',')
                header= ('ID','Designation','Description','Serial #')
                writer.writerow(header)
                for item in data:
                    writer.writerow(item)
            data_file.close()
            data_path=os.path.join(curDir, 'sqlite', 'devices'+'.csv')
            return send_file(data_path, attachment_filename='devices.csv', as_attachment=True)
        
        elif request.form['action'] == 'Download Data':
            lite_db.connect_lite('lora')
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
    my_thread.start()
    app.run(host='0.0.0.0', threaded=True)
