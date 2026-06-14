import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import heapq
from datetime import datetime
try:
    import matplotlib.pyplot as plt
except:
    plt = None
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB = True
except:
    REPORTLAB = False
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("hospital.db")
        self.cur = self.conn.cursor()
        self.cur.execute
        self.cur.execute
        self.cur.execute
        self.conn.commit()
class Person:
    def __init__(self, name, age, blood):
        self.name = name
        self.age = age
        self.blood = blood
class Donor(Person):
    def __init__(self, name, age, blood, organ):
        super().__init__(name, age, blood)
        self.organ = organ
class Recipient(Person):
    def __init__(self, name, age, blood, organ, urgency):
        super().__init__(name, age, blood)
        self.organ = organ
        self.urgency = urgency
class MatchMaker:
    compatibility = {
        "O-": ["O-", "O+", "A+", "A-", "B+", "B-", "AB+", "AB-"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"]
    }
    def score(self, donor, recipient):
        score = 0
        if donor[4].lower() == recipient[4].lower():
            score += 50
        if recipient[3] in self.compatibility.get(donor[3], []):
            score += 30
        score += min(int(recipient[5]) * 2, 20)
        return score
class App:
    def __init__(self, root):
        self.db = Database()
        self.matcher = MatchMaker()
        self.root = root
        self.root.title("Hospital Organ Donation Dashboard")
        self.root.geometry("1200x700")
        self.login_screen()
    def login_screen(self):
        self.login = tk.Frame(self.root)
        self.login.pack(fill="both", expand=True)
        tk.Label(
            self.login,
            text="HOSPITAL LOGIN",
            font=("Arial", 22, "bold")
        ).pack(pady=20)
        tk.Label(self.login, text="Username").pack()
        self.user = tk.Entry(self.login)
        self.user.pack()
        tk.Label(self.login, text="Password").pack()
        self.password = tk.Entry(self.login, show="*")
        self.password.pack()
        tk.Button(
            self.login,
            text="Login",
            command=self.check_login
        ).pack(pady=10)
    def check_login(self):
        if self.user.get() == "admin" and self.password.get() == "1234":
            self.login.destroy()
            self.main_ui()
        else:
            messagebox.showerror("Error", "Invalid Login")
    def main_ui(self):
        title = tk.Label(
            self.root,
            text="ORGAN DONATION MANAGEMENT SYSTEM",
            font=("Arial", 18, "bold"),
            bg="lightblue"
        )
        title.pack(fill="x")
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)
        self.dashboard = tk.Frame(self.tabs)
        self.donor_tab = tk.Frame(self.tabs)
        self.recipient_tab = tk.Frame(self.tabs)
        self.match_tab = tk.Frame(self.tabs)
        self.history_tab = tk.Frame(self.tabs)
        self.tabs.add(self.dashboard, text="Dashboard")
        self.tabs.add(self.donor_tab, text="Donors")
        self.tabs.add(self.recipient_tab, text="Recipients")
        self.tabs.add(self.match_tab, text="Matching")
        self.tabs.add(self.history_tab, text="History")
        self.build_dashboard()
        self.build_donor_tab()
        self.build_recipient_tab()
        self.build_match_tab()
        self.build_history_tab()
    def build_dashboard(self):
        self.stats = tk.Label(self.dashboard, font=("Arial", 15))
        self.stats.pack(pady=20)
        tk.Button(
            self.dashboard,
            text="Blood Group Analytics",
            command=self.show_chart
        ).pack()
        tk.Button(
            self.dashboard,
            text="Export PDF Report",
            command=self.export_pdf
        ).pack(pady=10)
        self.refresh_dashboard()
    def refresh_dashboard(self):
        donors = self.db.cur.execute(
            "SELECT COUNT(*) FROM donors"
        ).fetchone()[0]
        recipients = self.db.cur.execute(
            "SELECT COUNT(*) FROM recipients"
        ).fetchone()[0]
        matches = self.db.cur.execute(
            "SELECT COUNT(*) FROM history"
        ).fetchone()[0]
        self.stats.config(
            text=f"Total Donors: {donors}\n"
                 f"Total Recipients: {recipients}\n"
                 f"Match Records: {matches}"
        )
    def build_donor_tab(self):
        labels = ["Name", "Age", "Blood", "Organ"]
        self.d_entries = []
        for i, txt in enumerate(labels):
            tk.Label(self.donor_tab, text=txt).grid(row=i, column=0)
            e = tk.Entry(self.donor_tab)
            e.grid(row=i, column=1)
            self.d_entries.append(e)
        tk.Button(
            self.donor_tab,
            text="Add Donor",
            command=self.add_donor
        ).grid(row=5, column=1)
    def add_donor(self):
        vals = [e.get() for e in self.d_entries]
        self.db.cur.execute(
            "INSERT INTO donors(name,age,blood,organ) VALUES(?,?,?,?)",
            vals
        )
        self.db.conn.commit()
        self.refresh_dashboard()
        messagebox.showinfo("Success", "Donor Added")
    def build_recipient_tab(self):
        labels = ["Name", "Age", "Blood", "Organ Needed", "Urgency"]
        self.r_entries = []
        for i, txt in enumerate(labels):
            tk.Label(self.recipient_tab, text=txt).grid(row=i, column=0)
            e = tk.Entry(self.recipient_tab)
            e.grid(row=i, column=1)
            self.r_entries.append(e)
        tk.Button(
            self.recipient_tab,
            text="Add Recipient",
            command=self.add_recipient
        ).grid(row=6, column=1)
    def add_recipient(self):
        vals = [e.get() for e in self.r_entries]
        self.db.cur.execute(
            "INSERT INTO recipients(name,age,blood,organ,urgency) VALUES(?,?,?,?,?)",
            vals
        )
        self.db.conn.commit()
        self.refresh_dashboard()
        messagebox.showinfo("Success", "Recipient Added")
    def build_match_tab(self):
        tk.Button(
            self.match_tab,
            text="Find Matches",
            command=self.find_matches
        ).pack()
        self.tree = ttk.Treeview(
            self.match_tab,
            columns=("Donor", "Recipient", "Score"),
            show="headings"
        )
        for c in ("Donor", "Recipient", "Score"):
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
    def find_matches(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        donors = self.db.cur.execute(
            "SELECT * FROM donors"
        ).fetchall()
        recipients = self.db.cur.execute(
            "SELECT * FROM recipients"
        ).fetchall()
        queue = []
        for r in recipients:
            heapq.heappush(queue, (-int(r[5]), r))
        while queue:
            _, recipient = heapq.heappop(queue)
            for donor in donors:
                score = self.matcher.score(donor, recipient)
                if score >= 60:
                    self.tree.insert(
                        "",
                        "end",
                        values=(donor[1], recipient[1], score)
                    )
                    self.db.cur.execute(
                        "INSERT INTO history(donor,recipient,score,date) VALUES(?,?,?,?)",
                        (
                            donor[1],
                            recipient[1],
                            score,
                            str(datetime.now())
                        )
                    )
        self.db.conn.commit()
        self.load_history()
        self.refresh_dashboard()
    def build_history_tab(self):
        self.history = ttk.Treeview(
            self.history_tab,
            columns=("Donor", "Recipient", "Score", "Date"),
            show="headings"
        )
        for c in ("Donor", "Recipient", "Score", "Date"):
            self.history.heading(c, text=c)
        self.history.pack(fill="both", expand=True)
        self.load_history()
    def load_history(self):
        for i in self.history.get_children():
            self.history.delete(i)
        rows = self.db.cur.execute(
            "SELECT donor,recipient,score,date FROM history"
        ).fetchall()
        for row in rows:
            self.history.insert("", "end", values=row)
    def show_chart(self):
        if plt is None:
            messagebox.showerror(
                "Missing Package",
                "pip install matplotlib"
            )
            return
        rows = self.db.cur.execute(
            "SELECT blood,COUNT(*) FROM donors GROUP BY blood"
        ).fetchall()
        if not rows:
            return
        labels = [x[0] for x in rows]
        values = [x[1] for x in rows]
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.title("Blood Group Distribution")
        plt.show()
    def export_pdf(self):
        if not REPORTLAB:
            messagebox.showerror(
                "Missing Package",
                "pip install reportlab"
            )
            return
        pdf = SimpleDocTemplate("hospital_report.pdf")
        styles = getSampleStyleSheet()
        content = [
            Paragraph("Hospital Organ Donation Report", styles["Title"]),
            Spacer(1, 12)
        ]
        rows = self.db.cur.execute(
            "SELECT donor,recipient,score,date FROM history"
        ).fetchall()
        for r in rows:
            content.append(
                Paragraph(
                    f"Donor: {r[0]} | Recipient: {r[1]} | Score: {r[2]}",
                    styles["BodyText"]
                )
            )
        pdf.build(content)
        messagebox.showinfo(
            "Success",
            "hospital_report.pdf created"
        )
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()