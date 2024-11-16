import os
import json
import joblib
import requests
import pandas as pd

from openai import OpenAI
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
load_dotenv()


openai_client = OpenAI(
  organization='org-9FWgnQtl6zzQSOapo3hYZEQQ',
  project='proj_yTMKee6yHoVrEyzjTMKaHVPv',
)

auth_url = 'https://accounts.spotify.com/api/token'

def get_personality(prompt: str):
    # result = ""
    # stream = openai_client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role": "user", "content": prompt}],
    #     stream=True,
    # )
    # for chunk in stream:
    #     print('fdsfdsf', chunk.choices[0].delta.content)
    #     if chunk.choices[0].delta.content is not None:
    #         result += chunk.choices[0].delta.content
    personality = input(f'{prompt}\npersonality: ')
    return personality

def convert(access_token):
    data = []
    if not os.path.exists('data.json'):
        # Create the file with an empty dictionary if it doesn't exist
        with open('data.json', 'w') as file:
            json.dump({}, file)
    with open('data.json', 'r') as file:
        converted_data = json.load(file)
        if converted_data:
            data = converted_data
    folder_path = '/Users/bolortulgaseded/project/spotify_genres/train_model/data/syntheticParticipants'
    for filename in os.listdir(folder_path):
        try:
            participient = filename.replace('.txt', '')
            # Check if the file is a text file
            if filename.endswith('.txt') and not any(i['participient'] == participient for i in converted_data):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as file:
                    content = file.read()
                    personality = get_personality(content)
                    if personality == 'stop':
                        with open('data.json', 'w') as json_file:
                            json.dump(data, json_file, indent=4)
                        break
                    tracks = pd.read_csv(os.path.join(folder_path, filename.replace('txt','csv'))).fillna(value='')
                    print(len(tracks))
                    for _, tracks_row in tracks.iterrows():
                        print(tracks_row)
                        headers = {"Authorization": f"Bearer {access_token}"}
                        response = requests.get(f'https://api.spotify.com/v1/audio-features/{tracks_row["Spotify Track Id"]}', headers=headers)
                        features = response.json()
                        print(features)
                        if 'error' in features.keys():
                            with open('data.json', 'w') as json_file:
                                json.dump(data, json_file, indent=4)
                            break
                        
                        print(len(data)/30)
                        del features['analysis_url']
                        del features['type']
                        del features['id']
                        del features['uri']
                        del features['track_href']
                        del features['time_signature']
                        data.append({
                            'participient': participient,
                            'personality': personality,
                            'features': features
                        })

        except Exception:
            with open('data.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)

    with open('data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    X = data.drop(columns=['personality_type'])
    y = data['personality_type']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Initialize and train the classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    print("Classification Report:\n", classification_report(y_test, y_pred))
    print("Accuracy:", accuracy_score(y_test, y_pred))

    joblib.dump(model, 'random_forest_model.joblib')



if __name__ == '__main__':
    data = {
        'grant_type': 'client_credentials',
        'client_id': 'f55bea887a4443b4b81dac5b70630ea2',
        'client_secret': '6c057c30b75744cf95a6383406f47a9d',
    }
    auth_response = requests.post(auth_url, data=data)
    access_token = auth_response.json().get('access_token')
    convert(access_token)