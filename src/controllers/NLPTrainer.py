import os
import json
import joblib
from typing import List, Union, Dict
from threading import Thread, get_ident
from datetime import datetime
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from src.helpers.config import STORAGE_PATH


class NLPTrainer:
    def __init__(self) -> None:
        self._storage_path = STORAGE_PATH
        if not os.path.exists(self._storage_path):
            os.makedirs(self._storage_path)
        self._status_path = os.path.join(self._storage_path, "model_status.json")
        self._model_path = os.path.join(self._storage_path, "model_pickle.joblib")
        
        # check for status
        if os.path.exists(self._status_path):
            with open(self._status_path) as f:
                self.model_status = json.load(f)
        
        else:
            self.model_status = {"status": "No Model Found",
                                "timestamp": datetime.now().isoformat(), 
                                "classes": [], 
                                "evaluation": {}}

        # check for model
        if os.path.exists(self._model_path):
            self.model = joblib.load(self._model_path)
            
        else:
            self.model = None
            
        self._running_threads = []
        self._pipeline = None
        

    def _update_status(self, status: str, classes: List[str] = [], evaluation: Dict = {}) -> None:
        self.model_status['status'] = status
        self.model_status['timestamp'] = datetime.now().isoformat()
        self.model_status['classes'] = classes
        self.model_status['evaluation'] = evaluation

        with open(self._status_path, 'w+') as file:
            json.dump(self.model_status, file, indent=2)
            
            
    def _train_job(self, X_train: List[str], y_train: List[Union[str, int]], 
                X_test: List[str], y_test: List[Union[str, int]]):
        # Train the Model
        self._pipeline.fit(X_train, y_train)
        
        # Evaluate the Model
        report = classification_report(y_test, self._pipeline.predict(X_test), output_dict=True, zero_division=0)
        classes = self._pipeline.classes_.tolist()
        
        # Update Model Status
        self._update_status(status="Model Ready", classes=classes, evaluation=report)
        
        # Save the Model to a File
        joblib.dump(self._pipeline, self._model_path, compress=9)
        
        # Cleanup & Free Memory
        self.model = self._pipeline
        self._pipeline = None
        
        # Remove Completed Thread
        thread_id = get_ident()
        for i, t in enumerate(self._running_threads):
            if t.ident == thread_id:
                self._running_threads.pop(i)
                break
        
        
    def train(self, texts: List[str], labels: List[Union[str, int]]) -> None:
        if len(self._running_threads):
            raise Exception("A Training Process is already running. Please wait")
        
        # Split & Train
        X_train, X_test, y_train, y_test = train_test_split(texts, labels)
        clf = LogisticRegression()
        vec = TfidfVectorizer(stop_words='english',
                            min_df=0.01, max_df=0.35, ngram_range=(1, 2))
        self._pipeline = make_pipeline(vec, clf)

        # Update model status
        self.model = None
        self._update_status("Training")

        # Thread for training 
        t = Thread(target=self._train_job, args=(X_train, y_train, X_test, y_test))
        self._running_threads.append(t)
        t.start()
        
        
    def predict(self, texts: List[str]) -> List[Dict]:
        response = []
        if self.model:
            probs = self.model.predict_proba(texts)
            for i, row in enumerate(probs):
                row_pred = {}
                row_pred['text'] = texts[i]
                row_pred['predictions'] = {cls: round(float(prob), 3) for cls, prob in zip(self.model_status['classes'], row)}
                response.append(row_pred)
        else:
            raise Exception("No Trained model was found.")
        return response
    
    
    def get_status(self) -> Dict:
        return self.model_status
