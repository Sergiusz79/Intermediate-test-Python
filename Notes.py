import json
import csv
from datetime import datetime

class Note: # Model - MVC, представляет одну заметку.
    def __init__(self, note_id, title, body, timestamp=None): # Инициализация заметки
        self.note_id = note_id
        self.title = title
        self.body = body
        self.timestamp = timestamp or datetime.now().isoformat() #Если timestamp не указан, используется текущее время.

    def update(self, title=None, body=None): # Обновление заголовка и/или тела заметки, если переданы новые значения.
        if title:
            self.title = title
        if body:
            self.body = body
        self.timestamp = datetime.now().isoformat() # Обновляет временную метку изменения.

    def to_dict(self): # Преобразует заметку в словарь для сохранения в файле.
        return {
            "id": self.note_id,
            "title": self.title,
            "body": self.body,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_dict(data): # Создаёт объект Note из словаря.
        return Note(data["id"], data["title"], data["body"], data["timestamp"])

class NoteManager: # Controller - MVC, управляет списком заметок, их сохранением и загрузкой.

    def __init__(self, storage_file, storage_format="json"): # Принимает путь к файлу хранения заметок и формат, загружает заметки из файла.
        self.storage_file = storage_file
        self.storage_format = storage_format
        self.notes = self.load_notes()

    def load_notes(self): # Загружает заметки из файла 'storage_file', возвращает список объектов
        try:
            with open(self.storage_file, "r", encoding="utf-8") as file:
                if self.storage_format == "json":
                    return [Note.from_dict(note) for note in json.load(file)]
                elif self.storage_format == "csv":
                    reader = csv.DictReader(file, delimiter=';')
                    return [Note.from_dict(row) for row in reader]
        except FileNotFoundError:
            return []
        
    def save_notes(self): # Сохраняет список заметок в файл
        with open(self.storage_file, "w", encoding="utf-8") as file:
            if self.storage_format == "json":
                json.dump([note.to_dict() for note in self.notes], file, ensure_ascii=False, indent=4)
            elif self.storage_format == "csv":
                writer = csv.DictWriter(file, fieldnames=["id", "title", "body", "timestamp"], delimiter=';')
                writer.writeheader()
                for note in self.notes:
                    writer.writerow(note.to_dict())

    def create_note(self, title, body): # Создаёт новую заметку и добавляет её в список
        note_id = len(self.notes) + 1
        new_note = Note(note_id, title, body)
        self.notes.append(new_note)
        self.save_notes() # и сохраняет 

    def list_notes(self, start_date=None, end_date=None): # Cписок заметок с возможностью фильтрации по дате
        filtered_notes = self.notes
        if start_date:
            start_date = datetime.fromisoformat(start_date)
            filtered_notes = [note for note in filtered_notes if datetime.fromisoformat(note.timestamp) >= start_date]
        if end_date:
            end_date = datetime.fromisoformat(end_date)
            filtered_notes = [note for note in filtered_notes if datetime.fromisoformat(note.timestamp) <= end_date]
        return filtered_notes
    
    def get_note_by_id(self, note_id): # Поиск заметки по id
        for note in self.notes:
            if note.note_id == note_id:
                return note
        return None
    
    def update_note(self, note_id, title=None, body=None): # Обновление заголовока/тела заметки по id
        note = self.get_note_by_id(note_id)
        if note:
            note.update(title, body)
            self.save_notes()
            return True
        return False
    
    def delete_note_by_id(self, note_id): # Удаление по id
        note = self.get_note_by_id(note_id)
        if note:
            self.notes.remove(note)
            self.save_notes()
            return True
        return False
    
class NoteView: # Viev - MVC, отвечает за взаимодействие с пользователем

    def __init__(self, manager): # Принимает объект NoteManager для управления заметками
        self.manager = manager

    def display_menu(self): #Основное меню
        while True:
            print("\n1. Create note")
            print("2. List notes")
            print("3. View note")
            print("4. Edit note")
            print("5. Delete note")
            print("6. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                self.create_note()
            elif choice == "2":
                self.list_notes()
            elif choice == "3":
                self.view_note()
            elif choice == "4":
                self.edit_note()
            elif choice == "5":
                self.delete_note()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice, try again.")

    def create_note(self): # Запрашивает у пользователя заголовок и тело, создаёт новую заметку
        title = input("Enter title: ")
        body = input("Enter body: ")
        self.manager.create_note(title, body)
        print("Note created.")

    def list_notes(self): # Выводит список заметок с возможной фильтрацией по дате
        start_date = input("Enter start date (YYYY-MM-DD) or leave blank: ") or None
        end_date = input("Enter end date (YYYY-MM-DD) or leave blank: ") or None
        notes = self.manager.list_notes(start_date, end_date)
        for note in notes:
            print(f"ID: {note.note_id}, Title: {note.title}, Last Modified: {note.timestamp}")

    def view_note(self): # Позволяет посмотреть заметку по id
        note_id = int(input("Enter note ID: "))
        note = self.manager.get_note_by_id(note_id)
        if note:
            print(f"ID: {note.note_id}\nTitle: {note.title}\nBody: {note.body}\nLast Modified: {note.timestamp}")
        else:
            print("Note not found.")

    def edit_note(self): # Позволяет редактировать заголовок/текст заметки
        note_id = int(input("Enter note ID: "))
        title = input("Enter new title (leave blank to keep current): ")
        body = input("Enter new body (leave blank to keep current): ")
        if self.manager.update_note(note_id, title, body):
            print("Note updated.")
        else:
            print("Note not found.")

    def delete_note(self): # Удаляет заметку по id
        note_id = int(input("Enter note ID: "))
        if self.manager.delete_note_by_id(note_id):
            print("Note deleted.")
        else:
            print("Note not found.")

def main(): # Создаёт объект NoteManager и NoteView, затем запускает меню
    manager = NoteManager("notes.json")
    view = NoteView(manager)
    view.display_menu()

if __name__ == "__main__":
    main()