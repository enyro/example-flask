from flask import Flask, request, jsonify, send_file
import numpy as np 
import json
from keras.models import model_from_json
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)
 
with open('model/model_i.json', 'r') as json_file:
    loaded_model_json = json_file.read()

loaded_model = model_from_json(loaded_model_json)
 
loaded_model.load_weights("model/model_i_weights.weights.h5")

required_columns = [
    'duration',
    'protocol_type',
    'src_bytes',
    'dst_bytes',
    'land',
    'wrong_fragment',
    'urgent',
    'hot',
    'num_failed_logins',
    'logged_in',
    'lnum_compromised',
    'lroot_shell',
    'lsu_attempted',
    'lnum_root',
    'lnum_file_creations',
    'lnum_shells',
    'lnum_access_files',
    'is_guest_login',
    'count',
    'srv_count',
    'serror_rate',
    'srv_serror_rate',
    'rerror_rate',
    'srv_rerror_rate',
    'same_srv_rate',
    'diff_srv_rate',
    'srv_diff_host_rate',
    'dst_host_count',
    'dst_host_srv_count',
    'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate',
    'dst_host_serror_rate',
    'dst_host_srv_serror_rate',
    'dst_host_rerror_rate',
    'dst_host_srv_rerror_rate',
    'service',
    'flag'
]
training_columns = [
    'duration',
    'protocol_type',
    'src_bytes',
    'dst_bytes',
    'land',
    'wrong_fragment',
    'urgent',
    'hot',
    'num_failed_logins',
    'logged_in',
    'lnum_compromised',
    'lroot_shell',
    'lsu_attempted',
    'lnum_root',
    'lnum_file_creations',
    'lnum_shells',
    'lnum_access_files',
    'is_guest_login',
    'count',
    'srv_count',
    'serror_rate',
    'srv_serror_rate',
    'rerror_rate',
    'srv_rerror_rate',
    'same_srv_rate',
    'diff_srv_rate',
    'srv_diff_host_rate',
    'dst_host_count',
    'dst_host_srv_count',
    'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate',
    'dst_host_serror_rate',
    'dst_host_srv_serror_rate',
    'dst_host_rerror_rate',
    'dst_host_srv_rerror_rate',
    'service_encoded',
    'flag_encoded'
]
flag_mapping = {
            'OTH': 0,
            'REJ': 1,
            'RSTO': 2,
            'RSTOS0': 3,
            'RSTR': 4,
            'S0': 5,
            'S1': 6,
            'S2': 7,
            'S3': 8,
            'SF': 9,
            'SH': 10
        }
 
with open('services.json', "r") as json_file:
    service_mapping = json.load(json_file) 

def handle_exception(e): 
    response = jsonify({"code":0, "error": "Internal Server Error"})
    response.status_code = 200  
    return response

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        json_data = request.json  

        if json_data['protocol_type'] == 'tcp':
            json_data['protocol_type'] = 1
        elif json_data['protocol_type'] == 'udp':
            json_data['protocol_type'] = 2
        elif json_data['protocol_type'] == 'icmp':
            json_data['protocol_type'] = 3
        else :
            json_data['protocol_type'] = 0
 
        if json_data['flag'] in flag_mapping:
            json_data['flag_encoded'] = flag_mapping[json_data['flag']]
        else:
            json_data['flag_encoded'] = -1
     
        if json_data['service'] in service_mapping:
            json_data['service_encoded'] = service_mapping[json_data['service']]
        else:
            json_data['service_encoded'] = -1

        del json_data['flag']
        del json_data['service'] 

        X = np.array([
            json_data['duration'],
            json_data['protocol_type'],
            json_data['src_bytes'],
            json_data['dst_bytes'],
            json_data['land'],
            json_data['wrong_fragment'],
            json_data['urgent'],
            json_data['hot'],
            json_data['num_failed_logins'],
            json_data['logged_in'],
            json_data['lnum_compromised'],
            json_data['lroot_shell'],
            json_data['lsu_attempted'],
            json_data['lnum_root'],
            json_data['lnum_file_creations'],
            json_data['lnum_shells'],
            json_data['lnum_access_files'],
            json_data['is_guest_login'],
            json_data['count'],
            json_data['srv_count'],
            json_data['serror_rate'],
            json_data['srv_serror_rate'],
            json_data['rerror_rate'],
            json_data['srv_rerror_rate'],
            json_data['same_srv_rate'],
            json_data['diff_srv_rate'],
            json_data['srv_diff_host_rate'],
            json_data['dst_host_count'],
            json_data['dst_host_srv_count'],
            json_data['dst_host_same_srv_rate'],
            json_data['dst_host_diff_srv_rate'],
            json_data['dst_host_same_src_port_rate'],
            json_data['dst_host_srv_diff_host_rate'],
            json_data['dst_host_serror_rate'],
            json_data['dst_host_srv_serror_rate'],
            json_data['dst_host_rerror_rate'],
            json_data['dst_host_srv_rerror_rate'],
            json_data['service_encoded'],
            json_data['flag_encoded']
        ]) 
        X = X.reshape(1, -1)
        predictions = loaded_model.predict(X)
        pred_value = ''
        if predictions[0] == 1 :
            pred_value = 'Bad'
        else :
            pred_value = 'Good'

        return jsonify({'code':1, 'prediction': pred_value}) 
    except Exception as e:
        return handle_exception(e) 

@app.route('/api/csv_predict', methods=['POST'])
def csv_predict():
    try:
        if 'file' not in request.files:
            return jsonify({"code":0, "error": 'No file part'}) 
        
        file = request.files['file']
        
        # Check if the file is CSV
        if file.filename == '':
            return jsonify({"code":0, "error":  'No selected file'}) 
        
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            if set(required_columns).issubset(df.columns):
                df.loc[df['protocol_type'] == 'tcp', 'protocol_type'] = 1
                df.loc[df['protocol_type'] == 'udp', 'protocol_type'] = 2
                df.loc[df['protocol_type'] == 'icmp', 'protocol_type'] = 3

                df['flag_encoded'] = df['flag'].map(flag_mapping)
                df['service_encoded'] = df['service'].map(service_mapping)
                df = df[training_columns] 

                predictions = loaded_model.predict(df)
                df['prediction'] = ['Bad' if pred == 1 else 'Good' for pred in predictions]

                csv_text = df.to_csv(index=False)
                return jsonify({"code":1, "csv":  csv_text}) 
            else:
                return jsonify({"code":0, "error":  'CSV is missing some required columns'})   
        else:
            return jsonify({"code":0, "error":  'Invalid file format'})  
    except Exception as e:
        return handle_exception(e) 
 
if __name__ == '__main__':
    app.run(debug=True)
