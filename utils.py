import face_recognition as frg
import pickle as pkl
import os
import cv2
import numpy as np
import yaml
from collections import defaultdict

information = defaultdict(dict)
cfg = yaml.load(open('config.yaml','r'), Loader=yaml.FullLoader)
DATASET_DIR = cfg['PATH']['DATASET_DIR']
PKL_PATH = cfg['PATH']['PKL_PATH']

def get_database():
    with open(PKL_PATH, 'rb') as f:
        database = pkl.load(f)
    return database

def recognize(image, TOLERANCE):
    database = get_database()
    known_encoding = [database[id]['encoding'] for id in database.keys()]
    name = 'Tidak Diketahui'
    id = 'Tidak Diketahui'

    if image is None or len(image) == 0:
        return image, name, id

    # Pastikan gambar dalam format RGB
    if len(image.shape) == 2 or image.shape[2] != 3:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    face_locations = frg.face_locations(image)
    face_encodings = frg.face_encodings(image, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = frg.compare_faces(known_encoding, face_encoding, tolerance=TOLERANCE)
        distance = frg.face_distance(known_encoding, face_encoding)
        name = 'Tidak Diketahui'
        id = 'Tidak Diketahui'
        if True in matches:
            match_index = matches.index(True)
            name = database[match_index]['name']
            id = database[match_index]['id']
            distance = round(distance[match_index], 2)
            cv2.putText(image, str(distance), (left, top - 30), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
        else:
            cv2.putText(image, "Penyusup!", (left, top - 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
            print("ALERT: Penyusup terdeteksi!")
            
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
    return image, name, id

def isFaceExists(image):
    face_location = frg.face_locations(image)
    return len(face_location) > 0

def submitNew(name, id, image, old_idx=None):
    database = get_database()
    if type(image) != np.ndarray:
        image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), 1)

    isFaceInPic = isFaceExists(image)
    if not isFaceInPic:
        return -1

    encoding = frg.face_encodings(image)[0]
    existing_id = [database[i]['id'] for i in database.keys()]
    new_idx = old_idx if old_idx is not None else len(database)
    
    if old_idx is None and id in existing_id:
        return 0
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    database[new_idx] = {'image': image, 'id': id, 'name': name, 'encoding': encoding}
    
    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)
    
    return True

def get_info_from_id(id):
    database = get_database()
    for idx, person in database.items():
        if person['id'] == id:
            name = person['name']
            image = person['image']
            return name, image, idx
    return None, None, None

def deleteOne(id):
    database = get_database()
    id = str(id)
    for key, person in database.items():
        if person['id'] == id:
            del database[key]
            break
    with open(PKL_PATH, 'wb') as f:
        pkl.dump(database, f)
    return True

def build_dataset():
    counter = 0
    for image in os.listdir(DATASET_DIR):
        image_path = os.path.join(DATASET_DIR, image)
        image_name = image.split('.')[0]
        parsed_name = image_name.split('_')
        person_id = parsed_name[0]
        person_name = ' '.join(parsed_name[1:])
        if not image_path.endswith('.jpg'):
            continue
        image = frg.load_image_file(image_path)
        information[counter]['image'] = image
        information[counter]['id'] = person_id
        information[counter]['name'] = person_name
        information[counter]['encoding'] = frg.face_encodings(image)[0]
        counter += 1

    with open(os.path.join(DATASET_DIR, 'database.pkl'), 'wb') as f:
        pkl.dump(information, f)

if __name__ == "__main__":
    deleteOne(4)
