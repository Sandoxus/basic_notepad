import tkinter as tk
from tkinter import ttk, simpledialog, colorchooser, font, messagebox
import os
import re

class NoteApp:
    def __init__(self, root):
        # Styling
        self.root = root
        self.current_note = None  # Initialize current_note
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 12))
        self.style.configure('TListbox', font=('Arial', 12))
        self.style.configure('TText', font=('Arial', 12))

        root.title('Professional Note Taking App')
        root.geometry('800x600')  # Set start size of app
        
        # Binds
        root.bind('<Delete>', self.confirm_delete_note)
        root.bind('<Control-s>', self.save_note)

        # Menu
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='New Note', command=self.new_note)
        self.file_menu.add_command(label='Save Note', command=self.save_note)
        self.file_menu.add_command(label='Rename Note', command=self.rename_note)
        self.file_menu.add_command(label='Change Font Color', command=self.change_font_color)
        self.file_menu.add_command(label='Change Font Size', command=self.change_font_size)
        self.file_menu.add_command(label='Change Highlight Color', command=self.change_highlight_color)
        self.file_menu.add_command(label='Duplicate Note', command=self.duplicate_note)
        self.file_menu.add_command(label='Delete Note', command=self.menu_delete_note)

        # Layout: Frames
        left_frame = ttk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Note Title List
        self.note_list = tk.Listbox(left_frame, exportselection=False)
        self.note_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Note Text Area
        self.text = tk.Text(right_frame, wrap='word')
        self.text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Load existing notes
        self.notes = {}
        self.load_notes()

    def duplicate_note(self):
        original_title = self.note_list.get(tk.ACTIVE)
        if original_title:
            copy_title = self.get_unique_title(original_title)
            self.notes[copy_title] = self.notes[original_title]
            self.note_list.insert(tk.END, copy_title)
            self.save_note_as(copy_title)

    def get_unique_title(self, base_title):
        # Regular expression to match titles with an existing counter e.g., "note(1)"
        match = re.match(r"(.+?)\((\d+)\)$", base_title)
        if match:
            base_part = match.group(1)
            counter = int(match.group(2)) + 1
        else:
            base_part = base_title
            counter = 1

        new_title = f"{base_part}({counter})"
        while new_title in self.notes:
            counter += 1
            new_title = f"{base_part}({counter})"
        return new_title

    def save_note_as(self, title):
        self.notes[title] = self.text.get('1.0', tk.END)
        with open(title + '.txt', 'w') as file:
            file.write(self.notes[title])
       
    def change_font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter font size:", minvalue=8, maxvalue=72)
        if size:
            new_font = font.Font(family="Arial", size=size)
            self.text.config(font=new_font)
        
    def change_font_color(self):
        color = colorchooser.askcolor(title="Choose font color")[1]
        if color:
            self.text.config(fg=color)

    def change_highlight_color(self):
        color = colorchooser.askcolor(title="Choose highlight color")[1]
        if color:
            self.note_list.config(selectbackground=color)

    def on_note_select(self, event=None):
        if not event:  # Prevent issues when listbox is updated programmatically
            return

        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            self.current_note = widget.get(index)
            self.current_note = title
            self.text.delete('1.0', tk.END)
            self.text.insert(tk.END, self.notes[title])
            print(f"Loaded note: {title}")

    def new_note(self):
        title = simpledialog.askstring('Note Title', 'Enter note title:')
        if title and title not in self.notes:
            self.notes[title] = ''
            self.note_list.insert(tk.END, title)
            self.note_list.select_set(tk.END)
            self.on_note_select()
            print(f"New note created: {title}")
            self.current_note = title  # Update current_note when a new note is created


    def save_note(self, event=None):
        title_to_save = self.current_note if self.current_note else self.note_list.get(tk.ACTIVE)
        try:
            if title_to_save:
                self.notes[title_to_save] = self.text.get('1.0', tk.END)
                with open(title_to_save + '.txt', 'w') as file:
                    file.write(self.notes[title_to_save])
                print(f"Note saved: {title_to_save}")
        except Exception as e:
            print(f"Error saving note {title_to_save}: {e}")

    def rename_note(self):
        current_title = self.note_list.get(tk.ACTIVE)
        if current_title:
            new_title = simpledialog.askstring('Rename Note', 'Enter new note title:', initialvalue=current_title)
            if new_title and new_title not in self.notes:
                self.notes[new_title] = self.notes.pop(current_title)
                self.note_list.delete(tk.ACTIVE)
                self.note_list.insert(tk.ACTIVE, new_title)
                os.rename(current_title + '.txt', new_title + '.txt')
                self.current_note = new_title
                print(f"Renamed note from {current_title} to {new_title}")

    def load_notes(self):
        try:
            for filename in os.listdir('.'):
                if filename.endswith('.txt'):
                    title = filename[:-4]
                    with open(filename, 'r') as file:
                        content = file.read()
                    self.notes[title] = content
                    self.note_list.insert(tk.END, title)
            print("Notes loaded successfully.")
        except Exception as e:
            print(f"Error loading notes: {e}")

    def menu_delete_note(self):
        selected = self.note_list.curselection()
        if selected:
            self.confirm_delete_note()

    def confirm_delete_note(self, event=None):
        selected = self.note_list.curselection()
        if selected:
            title = self.note_list.get(selected)
            response = messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?")
            if response:
                self.delete_note(title)

    def delete_note(self, title):
        # Remove from listbox and notes dictionary
        if title in self.notes:
            del self.notes[title]
            idx = self.note_list.get(0, tk.END).index(title)
            self.note_list.delete(idx)
            # Optional: Delete the note file
            if os.path.exists(title + '.txt'):
                os.remove(title + '.txt')

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = NoteApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        input("Press Enter to close...")
