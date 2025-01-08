import tkinter as tk
from tkinter import ttk, messagebox
from db_setup import setup_database
import sqlite3
from datetime import datetime

class EventManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stadium Management System")
        self.root.geometry("1000x600")

        setup_database()
        self.conn = sqlite3.connect('event_management.db')
        self.cursor = self.conn.cursor()
        self.relationship_handlers = RelationshipHandlers(self.cursor, self.conn)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.events_tab = ttk.Frame(self.notebook)
        self.tickets_tab = ttk.Frame(self.notebook)
        self.users_tab = ttk.Frame(self.notebook)
        self.ticket_history_tab = ttk.Frame(self.notebook)
        self.staff_tab = ttk.Frame(self.notebook)
        self.facilities_tab = ttk.Frame(self.notebook)
        self.equipment_tab = ttk.Frame(self.notebook)
        self.security_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.events_tab, text='Events')
        self.notebook.add(self.tickets_tab, text='Tickets')
        self.notebook.add(self.users_tab, text='Users')
        self.notebook.add(self.staff_tab, text='Staff')
        self.notebook.add(self.facilities_tab, text='Facilities')
        self.notebook.add(self.equipment_tab, text='Equipment')
        self.notebook.add(self.security_tab, text='Security')

        self.events_columns = ('ID', 'Name', 'Type', 'Start', 'End', 'Holder')
        self.tickets_columns = ('ID', 'Event ID', 'User ID', 'Type', 'Seat', 'Status')
        self.users_columns = ('ID', 'Name', 'Email')
        self.staff_columns = ('ID', 'Name', 'Email', 'Phone', 'Position', 'Start', 'End', 'Salary')
        self.facilities_columns = ('ID', 'Name', 'Status')
        self.equipment_columns = ('ID', 'Name', 'Status')
        self.security_columns = ('ID', 'Name', 'Status', 'Facility')
        
        self.buttons = {}

        self.setup_events_tab()
        self.setup_tickets_tab()
        self.setup_users_tab()
        self.setup_staff_tab()
        self.setup_facilities_tab()
        self.setup_equipment_tab()
        self.setup_security_tab()

    def setup_events_tab(self):
        self.events_tree = self.create_treeview(self.events_tab, self.events_columns)
        self.buttons['events'] = self.add_button_frame(self.events_tab, self.show_add_event_dialog, self.load_events, self.show_update_event_dialog, self.delete_event, self.lookup_staff_events)
        self.load_events()

    def setup_tickets_tab(self):
        self.tickets_tree = self.create_treeview(self.tickets_tab, self.tickets_columns)
        self.buttons['tickets'] = self.add_button_frame(self.tickets_tab, self.show_add_ticket_dialog, self.load_tickets, self.show_update_ticket_dialog, self.delete_ticket, None)
        self.load_tickets()

    def setup_users_tab(self):
        self.users_tree = self.create_treeview(self.users_tab, self.users_columns)
        self.buttons['users'] = self.add_button_frame(self.users_tab, self.show_add_user_dialog, self.load_users, self.show_update_user_dialog, self.delete_user, self.lookup_user_tickets)
        self.load_users()

    def setup_staff_tab(self):
        self.staff_tree = self.create_treeview(self.staff_tab, self.staff_columns)
        self.buttons['staff'] = self.add_button_frame(self.staff_tab, self.show_add_staff_dialog, self.load_staff, self.show_update_staff_dialog, self.delete_staff, self.lookup_staff_facilities)
        self.load_staff()

    def setup_facilities_tab(self):
        self.facilities_tree = self.create_treeview(self.facilities_tab, self.facilities_columns)
        self.buttons['facilities'] = self.add_button_frame(self.facilities_tab, self.show_add_facility_dialog, self.load_facilities, self.show_update_facility_dialog, self.delete_facility, self.lookup_facilities_events)
        self.load_facilities()

    def setup_equipment_tab(self):
        self.equipment_tree = self.create_treeview(self.equipment_tab, self.equipment_columns)
        self.buttons['equipment'] = self.add_button_frame(self.equipment_tab, self.show_add_equipment_dialog, self.load_equipment, self.show_update_equipment_dialog, self.delete_equipment, self.lookup_equipment_events)
        self.load_equipment()

    def setup_security_tab(self):
        self.security_tree = self.create_treeview(self.security_tab, self.security_columns)
        self.buttons['security'] = self.add_button_frame(self.security_tab, self.show_add_security_dialog, self.load_security, self.show_update_security_dialog, self.delete_security, None)
        self.load_security()

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(expand=True, fill='both', padx=5, pady=5)
        return tree
    
    def update_treeview(self, tree, columns, data):
            tree.delete(*tree.get_children())
            tree.config(columns=columns)
            for col in columns:
                tree.heading(col, text=col)
            for row in data:
                 tree.insert('', 'end', values=row)
    
    def add_button_frame(self, parent, add_command, refresh_command, update_command, delete_command, lookup_command):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=5, pady=5)
        add_btn = ttk.Button(btn_frame, text="Add", command=add_command)
        add_btn.pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Refresh", command=refresh_command).pack(side='left', padx=5)
        update_btn = ttk.Button(btn_frame, text="Update", command=update_command)
        update_btn.pack(side='left', padx=5)
        delete_btn = ttk.Button(btn_frame, text="Delete", command=delete_command)
        delete_btn.pack(side='left', padx=5)

        extra_btns = []
        if parent == self.facilities_tab:
            assign_staff_btn = ttk.Button(btn_frame, text="Assign Staff", 
                    command=self.show_assign_facility_staff_dialog)
            assign_staff_btn.pack(side='left', padx=5)
            assign_event_btn = ttk.Button(btn_frame, text="Assign to Event", 
                    command=self.show_assign_facility_event_dialog)
            assign_event_btn.pack(side='left', padx=5)
            extra_btns = [assign_staff_btn, assign_event_btn]
        if parent == self.equipment_tab:
            assign_event_btn = ttk.Button(btn_frame, text="Assign to Event",
                       command=self.show_assign_equipment_event_dialog)
            assign_event_btn.pack(side='left', padx=5)
            extra_btns = [assign_event_btn]
        
        lookup_btn = None
        if lookup_command is not None:
            lookup_btn = ttk.Button(btn_frame, text="Lookup", command=lookup_command)
            lookup_btn.pack(side='right', padx=5)

        return (add_btn, update_btn, delete_btn, lookup_btn) + tuple(extra_btns)
    
    def set_button_state(self, tab_name, state):
        if tab_name in self.buttons:
          buttons = self.buttons[tab_name]
          for btn in buttons:
              if btn:
                  btn.config(state=state)
    
    def load_events(self):
        self.cursor.execute("SELECT * FROM Kravtsov_Events")
        data = self.cursor.fetchall()
        self.update_treeview(self.events_tree, self.events_columns, data)
        self.set_button_state('events', 'normal')

    def load_tickets(self):
        self.cursor.execute("SELECT * FROM Kravtsov_Tickets")
        data = self.cursor.fetchall()
        self.update_treeview(self.tickets_tree, self.tickets_columns, data)

    def load_users(self):
        self.cursor.execute("SELECT * FROM Kravtsov_Users")
        data = self.cursor.fetchall()
        self.update_treeview(self.users_tree, self.users_columns, data)
        self.set_button_state('users', 'normal')

    def load_staff(self):
        self.cursor.execute("SELECT * FROM Kravtsov_Staff")
        data = self.cursor.fetchall()
        self.update_treeview(self.staff_tree, self.staff_columns, data)
        self.set_button_state('staff', 'normal')

    def load_facilities(self):
        self.cursor.execute("SELECT * FROM Kravtsov_Facilities")
        data = self.cursor.fetchall()
        self.update_treeview(self.facilities_tree, self.facilities_columns, data)
        self.set_button_state('facilities', 'normal')

    def load_equipment(self):
         self.cursor.execute("SELECT * FROM Kravtsov_Equipment")
         data = self.cursor.fetchall()
         self.update_treeview(self.equipment_tree, self.equipment_columns, data)
         self.set_button_state('equipment', 'normal')

    def load_security(self):
        self.cursor.execute("SELECT * FROM Kravtsov_Security")
        data = self.cursor.fetchall()
        self.update_treeview(self.security_tree, self.security_columns, data)
        
    def show_add_event_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Event")

        fields = [
            ("Name:", None),
            ("Type:", ['sports', 'music', 'exhibition']),
            ("Event Start (YYYY-MM-DD HH:MM:SS):", None),
            ("Event End (YYYY-MM-DD HH:MM:SS):", None),
            ("Holder:", None)
        ]
        
        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)
        
        def save():
            try:
                query = """
                INSERT INTO Kravtsov_Events (event_name, event_type, event_start, event_end, event_holder)
                VALUES (?, ?, ?, ?, ?)
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Type:"].get(),
                    entries["Event Start (YYYY-MM-DD HH:MM:SS):"].get(),
                    entries["Event End (YYYY-MM-DD HH:MM:SS):"].get(),
                    entries["Holder:"].get()
                ))
                self.conn.commit()
                self.load_events()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def show_update_event_dialog(self):
        selected_item = self.events_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an event to update.")
            return

        event_id = self.events_tree.item(selected_item, "values")[0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Event")

        fields = [
            ("Name:", None),
            ("Type:", ['sports', 'music', 'exhibition']),
            ("Event Start (YYYY-MM-DD HH:MM:SS):", None),
            ("Event End (YYYY-MM-DD HH:MM:SS):", None),
            ("Holder:", None)
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        query = "SELECT * FROM Kravtsov_Events WHERE event_id = ?"
        event = self.cursor.execute(query, (event_id,)).fetchone()
        for i, value in enumerate(event[1:]):
            entries[fields[i][0]].insert(0, value if value is not None else "")

        def save():
            try:
                query = """
                UPDATE Kravtsov_Events
                SET event_name = ?, event_type = ?, event_start = ?, event_end = ?, event_holder = ?
                WHERE event_id = ?
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Type:"].get(),
                    entries["Event Start (YYYY-MM-DD HH:MM:SS):"].get(),
                    entries["Event End (YYYY-MM-DD HH:MM:SS):"].get(),
                    entries["Holder:"].get(),
                    event_id
                ))
                self.conn.commit()
                self.load_events()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_event(self):
        selected_item = self.events_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an event to delete.")
            return

        event_id = self.events_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this event?")
        if confirm:
            try:
                self.relationship_handlers.cleanup_relationships('Kravtsov_Events', 'event_id', event_id)
                query = "DELETE FROM Kravtsov_Events WHERE event_id = ?"
                self.cursor.execute(query, (event_id,))
                self.conn.commit()
                self.load_events()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

    def show_add_ticket_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Ticket")

        fields = [
            ("Event ID:", None),
            ("User ID:", None),
            ("Type:", ['one_day', 'multiple_days']),
            ("Seat:", ['sitting', 'sitting_vip', 'standing', 'standing_vip']),
            ("Status:", ['unsold', 'sold', 'expired'])
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        def save():
            try:
                query = """
                INSERT INTO Kravtsov_Tickets (event_id, user_id, ticket_type, seat, status)
                VALUES (?, ?, ?, ?, ?)
                """
                self.cursor.execute(query, (
                    entries["Event ID:"].get(),
                    entries["User ID:"].get(),
                    entries["Type:"].get(),
                    entries["Seat:"].get(),
                    entries["Status:"].get()
                ))
                self.conn.commit()
                self.load_tickets()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def show_update_ticket_dialog(self):
        selected_item = self.tickets_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a ticket to update.")
            return

        ticket_id = self.tickets_tree.item(selected_item, "values")[0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Ticket")

        fields = [
            ("Event ID:", None),
            ("User ID:", None),
            ("Type:", ['one_day', 'multiple_days']),
            ("Seat:", ['sitting', 'sitting_vip', 'standing', 'standing_vip']),
            ("Status:", ['unsold', 'sold', 'expired'])
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        query = "SELECT * FROM Kravtsov_Tickets WHERE ticket_id = ?"
        ticket = self.cursor.execute(query, (ticket_id,)).fetchone()
        for i, value in enumerate(ticket[1:]):
            entries[fields[i][0]].insert(0, value if value is not None else "")

        def save():
            try:
                query = """
                UPDATE Kravtsov_Tickets
                SET event_id = ?, user_id = ?, ticket_type = ?, seat = ?, status = ?
                WHERE ticket_id = ?
                """
                self.cursor.execute(query, (
                    entries["Event ID:"].get(),
                    entries["User ID:"].get(),
                    entries["Type:"].get(),
                    entries["Seat:"].get(),
                    entries["Status:"].get(),
                    ticket_id
                ))
                self.conn.commit()
                self.load_tickets()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_ticket(self):
        selected_item = self.tickets_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a ticket to delete.")
            return

        ticket_id = self.tickets_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this ticket?")
        if confirm:
            try:
                query = "DELETE FROM Kravtsov_Tickets WHERE ticket_id = ?"
                self.cursor.execute(query, (ticket_id,))
                self.conn.commit()
                self.load_tickets()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

    def show_add_user_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add User")

        fields = [
            ("Name:", None),
            ("Email:", None)
        ]

        entries = {}
        for i, (label, _) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        def save():
            try:
                query = "INSERT INTO Kravtsov_Users (name, email) VALUES (?, ?)"
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Email:"].get()
                ))
                self.conn.commit()
                self.load_users()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def show_update_user_dialog(self):
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to update.")
            return

        user_id = self.users_tree.item(selected_item, "values")[0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Update User")

        fields = [
            ("Name:", None),
            ("Email:", None)
        ]

        entries = {}
        for i, (label, _) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        query = "SELECT * FROM Kravtsov_Users WHERE user_id = ?"
        user = self.cursor.execute(query, (user_id,)).fetchone()
        for i, value in enumerate(user[1:]):
            entries[fields[i][0]].insert(0, value if value is not None else "")

        def save():
            try:
                query = """
                UPDATE Kravtsov_Users
                SET name = ?, email = ?
                WHERE user_id = ?
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Email:"].get(),
                    user_id
                ))
                self.conn.commit()
                self.load_users()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
    
    def lookup_user_tickets(self):
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to lookup tickets.")
            return

        user_id = self.users_tree.item(selected_item, "values")[0]

        self.set_button_state('users', 'disabled')
        
        query = """
        SELECT t.ticket_id, e.event_name, e.event_start, t.ticket_type, t.seat, t.status
        FROM Kravtsov_Tickets t
        JOIN Kravtsov_Events e ON t.event_id = e.event_id
        WHERE t.user_id = ?
        ORDER BY e.event_start
        """
        self.cursor.execute(query, (user_id,))
        data = self.cursor.fetchall()
        columns = ('Ticket ID', 'Event Name', 'Event Start', 'Ticket Type', 'Seat', 'Status')
        self.update_treeview(self.users_tree, columns, data)


    def delete_user(self):
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to delete.")
            return

        user_id = self.users_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this user?")
        if confirm:
            try:
                query = "DELETE FROM Kravtsov_Users WHERE user_id = ?"
                self.cursor.execute(query, (user_id,))
                self.conn.commit()
                self.load_users()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

    def show_add_staff_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Staff")

        fields = [
            ("Name:", None),
            ("Email:", None),
            ("Phone:", None),
            ("Position:", None),
            ("Schedule Start (HH:MM):", None),
            ("Schedule End (HH:MM):", None),
            ("Salary:", None)
        ]

        entries = {}
        for i, (label, _) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        def save():
            try:
                query = """
                INSERT INTO Kravtsov_Staff (staff_name, staff_email, phone_number, position, schedule_start, schedule_end, salary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Email:"].get(),
                    entries["Phone:"].get(),
                    entries["Position:"].get(),
                    entries["Schedule Start (HH:MM):"].get(),
                    entries["Schedule End (HH:MM):"].get(),
                    entries["Salary:"].get()
                ))
                self.conn.commit()
                self.load_staff()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def show_update_staff_dialog(self):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a staff member to update.")
            return

        staff_id = self.staff_tree.item(selected_item, "values")[0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Staff")

        fields = [
            ("Name:", None),
            ("Email:", None),
            ("Phone:", None),
            ("Position:", None),
            ("Schedule Start (HH:MM):", None),
            ("Schedule End (HH:MM):", None),
            ("Salary:", None)
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        query = "SELECT * FROM Kravtsov_Staff WHERE staff_id = ?"
        staff = self.cursor.execute(query, (staff_id,)).fetchone()
        for i, value in enumerate(staff[1:]):
            entries[fields[i][0]].insert(0, value if value is not None else "")

        def save():
            try:
                query = """
                UPDATE Kravtsov_Staff
                SET staff_name = ?, staff_email = ?, phone_number = ?, 
                    position = ?, schedule_start = ?, schedule_end = ?, salary = ?
                WHERE staff_id = ?
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Email:"].get(),
                    entries["Phone:"].get(),
                    entries["Position:"].get(),
                    entries["Schedule Start (HH:MM):"].get(),
                    entries["Schedule End (HH:MM):"].get(),
                    entries["Salary:"].get(),
                    staff_id
                ))
                self.conn.commit()
                self.load_staff()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def lookup_staff_events(self):
        selected_item = self.events_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an event to lookup available staff.")
            return

        event_id = self.events_tree.item(selected_item, "values")[0]
        self.set_button_state('events', 'disabled')

        query = """
        SELECT 
            s.staff_name,
            s.position,
            s.schedule_start,
            s.schedule_end
        FROM Kravtsov_Staff s
        JOIN Kravtsov_Events e ON e.event_id = ?
        WHERE
        CASE
            WHEN strftime('%H:%M', s.schedule_start) < strftime('%H:%M', s.schedule_end) THEN
                NOT (
                    strftime('%H:%M', e.event_end) <= strftime('%H:%M', s.schedule_start)
                    OR
                    strftime('%H:%M', e.event_start) > strftime('%H:%M', s.schedule_end)
                )
            ELSE
                NOT (
                    (strftime('%H:%M', e.event_end) <= strftime('%H:%M', s.schedule_start) 
                    AND strftime('%H:%M', e.event_start) < strftime('%H:%M', s.schedule_end))
                    OR
                    (strftime('%H:%M', e.event_start) > strftime('%H:%M', s.schedule_end) 
                    AND strftime('%H:%M', e.event_end) >= strftime('%H:%M', s.schedule_start))
                 )
        END
        ORDER BY e.event_start
        """
        self.cursor.execute(query, (event_id,))
        data = self.cursor.fetchall()
        columns = ('Staff Name', 'Position', 'Schedule Start', 'Schedule End')
        self.update_treeview(self.events_tree, columns, data)

    def lookup_staff_facilities(self):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a staff member to lookup facilities.")
            return

        staff_id = self.staff_tree.item(selected_item, "values")[0]
        self.set_button_state('staff', 'disabled')
        
        query = """
        SELECT f.facility_id, f.facility_name, f.facility_status
        FROM Kravtsov_Facilities f
        JOIN Kravtsov_Facilities_Staff fs ON f.facility_id = fs.facility_id
        WHERE fs.staff_id = ?
        """
        self.cursor.execute(query, (staff_id,))
        data = self.cursor.fetchall()
        columns = ('Facility ID', 'Facility Name', 'Facility Status')
        self.update_treeview(self.staff_tree, columns, data)

    def delete_staff(self):
        selected_item = self.staff_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a staff member to delete.")
            return

        staff_id = self.staff_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this staff member?")
        if confirm:
            try:
                self.relationship_handlers.cleanup_relationships('Kravtsov_Staff', 'staff_id', staff_id)
                query = "DELETE FROM Kravtsov_Staff WHERE staff_id = ?"
                self.cursor.execute(query, (staff_id,))
                self.conn.commit()
                self.load_staff()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

    def show_add_facility_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Facility")

        fields = [
            ("Name:", None),
            ("Status:", ['free', 'occupied', 'private'])
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        def save():
            try:
                query = """
                INSERT INTO Kravtsov_Facilities (facility_name, facility_status)
                VALUES (?, ?)
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Status:"].get()
                ))
                self.conn.commit()
                self.load_facilities()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)
    
    def show_update_facility_dialog(self):
        selected_item = self.facilities_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a facility to update.")
            return

        facility_id = self.facilities_tree.item(selected_item, "values")[0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Facility")

        fields = [
            ("Name:", None),
            ("Status:", ['free', 'occupied', 'private'])
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        query = "SELECT * FROM Kravtsov_Facilities WHERE facility_id = ?"
        facility = self.cursor.execute(query, (facility_id,)).fetchone()
        for i, value in enumerate(facility[1:]):
            entries[fields[i][0]].insert(0, value if value is not None else "")

        def save():
            try:
                query = """
                UPDATE Kravtsov_Facilities
                SET facility_name = ?, facility_status = ?
                WHERE facility_id = ?
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Status:"].get(),
                    facility_id
                ))
                self.conn.commit()
                self.load_facilities()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def lookup_facilities_events(self):
        selected_item = self.facilities_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a facility to lookup events.")
            return

        facility_id = self.facilities_tree.item(selected_item, "values")[0]

        self.set_button_state('facilities', 'disabled')
    
        query = """
        SELECT 
            e.event_id, e.event_name, e.event_type, 
            e.event_start, e.event_end,
            fe.usage_start, fe.usage_end,
            e.event_holder
        FROM Kravtsov_Facilities_Events fe
        JOIN Kravtsov_Events e ON e.event_id = fe.event_id
        WHERE fe.facility_id = ?
        ORDER BY fe.usage_start
        """
        self.cursor.execute(query, (facility_id,))
        data = self.cursor.fetchall()
        columns = ('Event ID', 'Event Name', 'Event Type', 'Event Start', 'Event End', 'Usage Start', 'Usage End', 'Event Holder')
        self.update_treeview(self.facilities_tree, columns, data)

    def delete_facility(self):
        selected_item = self.facilities_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a facility to delete.")
            return

        facility_id = self.facilities_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this facility?")
        if confirm:
            try:
                self.relationship_handlers.cleanup_relationships('Kravtsov_Facilities', 'facility_id', facility_id)
                query = "DELETE FROM Kravtsov_Facilities WHERE facility_id = ?"
                self.cursor.execute(query, (facility_id,))
                self.conn.commit()
                self.load_facilities()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

    def show_add_equipment_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Equipment")

        fields = [
            ("Name:", None),
            ("Status:", ['free', 'occupied'])
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        def save():
            try:
                query = """
                INSERT INTO Kravtsov_Equipment (item_name, item_status)
                VALUES (?, ?)
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Status:"].get()
                ))
                self.conn.commit()
                self.load_equipment()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def show_update_equipment_dialog(self):
        selected_item = self.equipment_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an equipment to update.")
            return

        equipment_id = self.equipment_tree.item(selected_item, "values")[0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Equipment")

        fields = [
            ("Name:", None),
            ("Status:", ['free', 'occupied'])
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        query = "SELECT * FROM Kravtsov_Equipment WHERE item_id = ?"
        equipment = self.cursor.execute(query, (equipment_id,)).fetchone()
        for i, value in enumerate(equipment[1:]):
            entries[fields[i][0]].insert(0, value if value is not None else "")

        def save():
            try:
                query = """
                UPDATE Kravtsov_Equipment
                SET item_name = ?, item_status = ?
                WHERE item_id = ?
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Status:"].get(),
                    equipment_id
                ))
                self.conn.commit()
                self.load_equipment()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def lookup_equipment_events(self):
        selected_item = self.equipment_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select equipment to lookup events.")
            return

        equipment_id = self.equipment_tree.item(selected_item, "values")[0]

        self.set_button_state('equipment', 'disabled')

        query = """
        SELECT 
            e.event_id, e.event_name, e.event_type,
            e.event_start, e.event_end,
            ee.usage_start, ee.usage_end,
            e.event_holder
        FROM Kravtsov_Equipment_Events ee
        JOIN Kravtsov_Events e ON e.event_id = ee.event_id
        WHERE ee.item_id = ?
        ORDER BY ee.usage_start
        """
        self.cursor.execute(query, (equipment_id,))
        data = self.cursor.fetchall()
        columns = ('Event ID', 'Event Name', 'Event Type', 'Event Start', 'Event End', 'Usage Start', 'Usage End', 'Event Holder')
        self.update_treeview(self.equipment_tree, columns, data)

    def delete_equipment(self):
        selected_item = self.equipment_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an equipment to delete.")
            return

        equipment_id = self.equipment_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this equipment?")
        if confirm:
            try:
                self.relationship_handlers.cleanup_relationships('Kravtsov_Equipment', 'item_id', equipment_id)
                query = "DELETE FROM Kravtsov_Equipment WHERE item_id = ?"
                self.cursor.execute(query, (equipment_id,))
                self.conn.commit()
                self.load_equipment()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

    def show_add_security_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Security")

        fields = [
            ("Name:", None),
            ("Status:", ['up', 'out_of_service', 'under_maintenance']),
            ("Facility ID:", None)
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        def save():
            try:
                query = """
                INSERT INTO Kravtsov_Security (sec_item_name, sec_item_status, facility_id)
                VALUES (?, ?, ?)
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Status:"].get(),
                    entries["Facility ID:"].get()
                ))
                self.conn.commit()
                self.load_security()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def show_update_security_dialog(self):
        selected_item = self.security_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a security item to update.")
            return

        security_id = self.security_tree.item(selected_item, "values")[0]
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Security")

        fields = [
            ("Name:", None),
            ("Status:", ['up', 'out_of_service', 'under_maintenance']),
            ("Facility ID:", None)
        ]

        entries = {}
        for i, (label, values) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if values:
                entries[label] = ttk.Combobox(dialog, values=values)
            else:
                entries[label] = ttk.Entry(dialog)
            entries[label].grid(row=i, column=1, padx=5, pady=5)

        query = "SELECT * FROM Kravtsov_Security WHERE sec_item_id = ?"
        security = self.cursor.execute(query, (security_id,)).fetchone()
        for i, value in enumerate(security[1:]):
            entries[fields[i][0]].insert(0, value if value is not None else "")

        def save():
            try:
                query = """
                UPDATE Kravtsov_Security
                SET sec_item_name = ?, sec_item_status = ?, facility_id = ?
                WHERE sec_item_id = ?
                """
                self.cursor.execute(query, (
                    entries["Name:"].get(),
                    entries["Status:"].get(),
                    entries["Facility ID:"].get(),
                    security_id
                ))
                self.conn.commit()
                self.load_security()
                dialog.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def delete_security(self):
        selected_item = self.security_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a security item to delete.")
            return

        security_id = self.security_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this security item?")
        if confirm:
            try:
                query = "DELETE FROM Kravtsov_Security WHERE sec_item_id = ?"
                self.cursor.execute(query, (security_id,))
                self.conn.commit()
                self.load_security()
            except sqlite3.Error as e:
                messagebox.showerror("Error", str(e))
    
    def show_assign_facility_staff_dialog(self):
        selected_facility = self.facilities_tree.selection()
        if not selected_facility:
            messagebox.showwarning("Warning", "Please select a facility first.")
            return

        facility_id = self.facilities_tree.item(selected_facility, "values")[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Staff to Facility")
        
        self.cursor.execute("SELECT staff_id, staff_name FROM Kravtsov_Staff")
        staff_list = self.cursor.fetchall()
        
        ttk.Label(dialog, text="Select Staff:").grid(row=0, column=0, padx=5, pady=5)
        staff_var = tk.StringVar()
        staff_combo = ttk.Combobox(dialog, textvariable=staff_var)
        staff_combo['values'] = [f"{id} - {name}" for id, name in staff_list]
        staff_combo.grid(row=0, column=1, padx=5, pady=5)
        
        def save():
            if not staff_var.get():
                messagebox.showwarning("Warning", "Please select a staff member.")
                return
                
            staff_id = int(staff_var.get().split(" - ")[0])
            if self.relationship_handlers.assign_staff_to_facility(facility_id, staff_id):
                dialog.destroy()
                self.load_facilities()
        
        ttk.Button(dialog, text="Assign", command=save).grid(row=1, column=0, columnspan=2, pady=10)

    def show_assign_facility_event_dialog(self):
        selected_facility = self.facilities_tree.selection()
        if not selected_facility:
            messagebox.showwarning("Warning", "Please select a facility first.")
            return

        facility_id = self.facilities_tree.item(selected_facility, "values")[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Facility to Event")
        self.cursor.execute("SELECT event_id, event_name FROM Kravtsov_Events")
        event_list = self.cursor.fetchall()
        
        ttk.Label(dialog, text="Select Event:").grid(row=0, column=0, padx=5, pady=5)
        event_var = tk.StringVar()
        event_combo = ttk.Combobox(dialog, textvariable=event_var)
        event_combo['values'] = [f"{id} - {name}" for id, name in event_list]
        event_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Usage Start (YYYY-MM-DD HH:MM:SS):").grid(row=1, column=0, padx=5, pady=5)
        start_entry = ttk.Entry(dialog)
        start_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Usage End (YYYY-MM-DD HH:MM:SS):").grid(row=2, column=0, padx=5, pady=5)
        end_entry = ttk.Entry(dialog)
        end_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save():
            if not event_var.get():
                messagebox.showwarning("Warning", "Please select an event.")
                return
                
            event_id = int(event_var.get().split(" - ")[0])
            if self.relationship_handlers.assign_facility_to_event(
                facility_id, event_id, start_entry.get(), end_entry.get()):
                dialog.destroy()
                self.load_facilities()
        
        ttk.Button(dialog, text="Assign", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def show_assign_equipment_event_dialog(self):
        selected_equipment = self.equipment_tree.selection()
        if not selected_equipment:
            messagebox.showwarning("Warning", "Please select equipment first.")
            return

        equipment_id = self.equipment_tree.item(selected_equipment, "values")[0]

        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Equipment to Event")

        self.cursor.execute("SELECT event_id, event_name FROM Kravtsov_Events")
        event_list = self.cursor.fetchall()

        ttk.Label(dialog, text="Select Event:").grid(row=0, column=0, padx=5, pady=5)
        event_var = tk.StringVar()
        event_combo = ttk.Combobox(dialog, textvariable=event_var)
        event_combo['values'] = [f"{id} - {name}" for id, name in event_list]
        event_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Usage Start (YYYY-MM-DD HH:MM:SS):").grid(row=1, column=0, padx=5, pady=5)
        start_entry = ttk.Entry(dialog)
        start_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Usage End (YYYY-MM-DD HH:MM:SS):").grid(row=2, column=0, padx=5, pady=5)
        end_entry = ttk.Entry(dialog)
        end_entry.grid(row=2, column=1, padx=5, pady=5)

        def save():
            if not event_var.get():
                messagebox.showwarning("Warning", "Please select an event.")
                return

            event_id = int(event_var.get().split(" - ")[0])
            if self.relationship_handlers.assign_equipment_to_event(
                    equipment_id, event_id, start_entry.get(), end_entry.get()):
                dialog.destroy()
                self.load_equipment()

        ttk.Button(dialog, text="Assign", command=save).grid(row=3, column=0, columnspan=2, pady=10)

class RelationshipHandlers:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def assign_staff_to_facility(self, facility_id, staff_id):
        try:
            check_query = """
            SELECT COUNT(*) FROM Kravtsov_Facilities_Staff
            WHERE facility_id = ? AND staff_id = ?
            """
            self.cursor.execute(check_query, (facility_id, staff_id))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showinfo("Info", "Staff is already assigned to this facility.")
                return False

            query = """
            INSERT INTO Kravtsov_Facilities_Staff (facility_id, staff_id)
            VALUES (?, ?)
            """
            self.cursor.execute(query, (facility_id, staff_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Staff assigned to facility successfully.")
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Could not assign staff to facility: {str(e)}")
            return False

    def assign_facility_to_event(self, facility_id, event_id, usage_start_str, usage_end_str):
        try:
            usage_start = datetime.strptime(usage_start_str, '%Y-%m-%d %H:%M:%S')
            usage_end = datetime.strptime(usage_end_str, '%Y-%m-%d %H:%M:%S')

            availability_query = """
            SELECT COUNT(*) FROM Kravtsov_Facilities_Events
            WHERE facility_id = ? AND NOT (
                usage_end <= ? OR usage_start >= ?
            )
            """
            self.cursor.execute(availability_query, (facility_id, usage_start_str, usage_end_str))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Facility is already in use during this time period.")
                return False

            query = """
            INSERT INTO Kravtsov_Facilities_Events (facility_id, event_id, usage_start, usage_end)
            VALUES (?, ?, ?, ?)
            """
            self.cursor.execute(query, (facility_id, event_id, usage_start_str, usage_end_str))

            update_status = """
            UPDATE Kravtsov_Facilities
            SET facility_status = 'occupied'
            WHERE facility_id = ?
            """
            self.cursor.execute(update_status, (facility_id,))


            self.conn.commit()
            messagebox.showinfo("Success", "Facility assigned to event successfully.")
            return True
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format.")
            return False
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Could not assign facility to event: {str(e)}")
            return False

    def assign_equipment_to_event(self, item_id, event_id, usage_start_str, usage_end_str):
          try:
            usage_start = datetime.strptime(usage_start_str.strip(), '%Y-%m-%d %H:%M:%S')
            usage_end = datetime.strptime(usage_end_str.strip(), '%Y-%m-%d %H:%M:%S')


            availability_query = """
            SELECT COUNT(*) FROM Kravtsov_Equipment_Events
            WHERE item_id = ? AND NOT (
                usage_end <= ? OR usage_start >= ?
            )
            """
            self.cursor.execute(availability_query, (item_id, usage_start_str, usage_end_str))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Equipment is already in use during this time period.")
                return False

            query = """
            INSERT INTO Kravtsov_Equipment_Events (item_id, event_id, usage_start, usage_end)
            VALUES (?, ?, ?, ?)
            """
            self.cursor.execute(query, (item_id, event_id, usage_start_str, usage_end_str))

            update_status = """
            UPDATE Kravtsov_Equipment
            SET item_status = 'occupied'
            WHERE item_id = ?
            """
            self.cursor.execute(update_status, (item_id,))

            self.conn.commit()
            messagebox.showinfo("Success", "Equipment assigned to event successfully.")
            return True
          except ValueError:
             messagebox.showerror("Error", "Invalid date/time format.")
             return False
          except sqlite3.Error as e:
             self.conn.rollback()
             messagebox.showerror("Error", f"Could not assign equipment to event: {str(e)}")
             return False

    def cleanup_relationships(self, table_name, id_column, id_value):
        relationship_tables = {
            'Kravtsov_Facilities': [
                ('Kravtsov_Facilities_Staff', 'facility_id'),
                ('Kravtsov_Facilities_Events', 'facility_id')
            ],
            'Kravtsov_Staff': [
                ('Kravtsov_Facilities_Staff', 'staff_id')
            ],
             'Kravtsov_Equipment': [
                ('Kravtsov_Equipment_Events', 'item_id')
            ],
            'Kravtsov_Events': [
                ('Kravtsov_Facilities_Events', 'event_id'),
                 ('Kravtsov_Equipment_Events', 'event_id')
            ]
        }

        if table_name in relationship_tables:
            for rel_table, rel_column in relationship_tables[table_name]:
                try:
                    query = f"DELETE FROM {rel_table} WHERE {rel_column} = ?"
                    self.cursor.execute(query, (id_value,))
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Could not clean up relationships: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EventManagementGUI(root)
    root.mainloop()