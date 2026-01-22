from backend.storage import load_tasks, save_tasks, load_settings, save_settings

class TaskManager:
    def __init__(self):
        self.tasks = load_tasks()
        self.settings = load_settings()

    def add_task(self, title, priority="Medium"):
        if title.strip():
            self.tasks.append({"title": title, "completed": False, "priority": priority})
            save_tasks(self.tasks)
            return True
        return False

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            save_tasks(self.tasks)

    def toggle_complete(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]['completed'] = not self.tasks[index]['completed']
            save_tasks(self.tasks)

    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t['completed']]
        save_tasks(self.tasks)

    def get_stats(self):
        total = len(self.tasks)
        done = len([t for t in self.tasks if t['completed']])
        percent = (done / total) if total > 0 else 0
        return done, total, percent

    def filter_tasks(self, query=""):
        if not query: return self.tasks
        return [t for t in self.tasks if query.lower() in t['title'].lower()]

    def set_theme(self, mode):
        self.settings["theme"] = mode
        save_settings(self.settings)