import json
import csv
from datetime import datetime

class Note:
    def __init__(self, note_id, title, body, timestamp=None):
        self.note_id = note_id
        self.title = title
        self.body = body
        self.timestamp = timestamp or datetime.now().isoformat()

    def update(self, title=None, body=None):
        if title:
            self.title = title
        if body:
            self.body = body
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.note_id,
            "title": self.title,
            "body": self.body,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_dict(data):
        return Note(data["id"], data["title"], data["body"], data["timestamp"])

class NoteManager:

def main(): 
