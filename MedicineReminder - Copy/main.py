import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry

import json
import os
import threading
import time
import schedule
import pywhatkit
import re

from datetime import datetime, timedelta
from plyer import notification

# --- MATPLOTLIB IMPORTS FOR CHART ---
import matplotlib
matplotlib.use('TkAgg')  # Force stable backend integration before imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- FILE STORAGE CONFIGURATION ----------------

FILE_NAME = "medicines.json"

if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w") as file:
        json.dump([], file)

# ---------------- CORE DATABASE UTILITIES ----------------

def load_json():
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except:
        return []

def save_json(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

# ---------------- WHATSAPP & BACKGROUND ENGINE ----------------

def send_whatsapp(name):
    # Dynamically reads the current user's number from the profile input box
    phone_number = phone_entry.get().strip()
    
    if not phone_number:
        print("WhatsApp warning: No recipient phone number provided in the user profile.")
        return

    message = f"\n💊 Medicine Reminder\n\nUser: {username_entry.get().strip()}\nMedicine : {name}\n\nPlease take your medicine on time.\n\nStay Healthy ❤️\n"
    send = datetime.now() + timedelta(minutes=1)
    
    try:
        # Optimized timing configurations to guarantee delivery before automatic closure
        pywhatkit.sendwhatmsg(
            phone_number,
            message,
            send.hour,
            send.minute,
            wait_time=25,       # Gives the browser 25 seconds to load completely
            tab_close=True,     # Keep auto-close active
            close_time=10       # Gives 10 seconds to submit the message before tab closes
        )
    except Exception as e:
        print("WhatsApp Notification Engine Exception Error:", e)

def play_sound():
    try:
        import winsound
        winsound.Beep(1000, 700)
    except:
        pass

def reminder_worker(name):
    medicines = load_json()
    for med in medicines:
        if med.get("name") == name and med.get("missed"):
            print(f"WhatsApp skipped because {name} is marked as MISSED.")
            return

    play_sound()
    try:
        notification.notify(
            title="💊 Medicine Reminder",
            message=f"Time to take {name}",
            timeout=10
        )
    except Exception as e:
        print("Desktop Notification System Error:", e)
    
    send_whatsapp(name)

def show_notification(name):
    threading.Thread(target=reminder_worker, args=(name,), daemon=True).start()

# ---------------- SCHEDULER ORCHESTRATION ----------------

def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=scheduler, daemon=True).start()

def schedule_all():
    medicines = load_json()
    schedule.clear()
    
    today = datetime.now().strftime("%d/%m/%Y")
    current_time = datetime.now().strftime("%H:%M")
    
    for medicine in medicines:
        try:
            med_date = medicine.get("date", "N/A")
            med_time = medicine.get("time", "N/A")
            med_name = medicine.get("name", "Unknown")
            
            if med_date == today and med_time >= current_time and not medicine.get("taken") and not medicine.get("missed"):
                schedule.every().day.at(med_time).do(
                    show_notification,
                    med_name
                )
        except Exception as e:
            print("Scheduling Engine Registration Failure:", e)

# ---------------- MATTE MAC EXECUTIVE GRAPH GENERATOR ----------------

def update_graph():
    medicines = load_json()
    med_units_map = {}
    
    for m in medicines:
        if m.get("taken"): 
            med_name = m.get("name", "Unknown").strip()
            dosage_str = m.get("dosage", "1")
            try:
                dosage_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", dosage_str)[0])
            except:
                dosage_val = 1.0  
                
            med_units_map[med_name] = med_units_map.get(med_name, 0) + dosage_val

    ax.clear()
    
    # Premium Mac-Style Minimalist Contrast Frame Panels
    fig.patch.set_facecolor('#1a1a1e')
    ax.set_facecolor('#0d0d0f')  
    ax.grid(axis='y', linestyle='--', alpha=0.15, color='#ffffff') 
    
    if not med_units_map:
        ax.text(0.5, 0.5, 'No Consumption Logged\n\n[Verify logged intake records to populate]', 
                ha='center', va='center', fontsize=11, color='#8e8e93', fontweight='normal')
        ax.set_title("Intake Metric Analytics", fontsize=13, fontweight='bold', pad=15, color='#ffffff')
        canvas.draw()
        return

    categories = list(med_units_map.keys())
    counts = list(med_units_map.values())
    
    # Premium Apple iOS Emerald Mint Palette
    bars = ax.bar(categories, counts, color='#30d158', width=0.4, edgecolor='#34c759', linewidth=1.5, zorder=3, alpha=0.9)
    
    ax.set_title("Total Logged Units Per Identifier", fontsize=13, fontweight='bold', pad=18, color='#ffffff')
    ax.set_ylabel("Quantity Logged", fontsize=10, fontweight='bold', color='#aeaeac')
    ax.set_xlabel("Logged Identifiers", fontsize=10, fontweight='bold', color='#aeaeac')
    
    # Clean up native structural border frames
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#2c2c2e')
    ax.spines['bottom'].set_color('#2c2c2e')

    plt.setp(ax.get_xticklabels(), rotation=12, horizontalalignment='right', fontsize=9, color='#ffffff')
    plt.setp(ax.get_yticklabels(), fontsize=9, color='#ffffff')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:g}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 6),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#30d158')
        
    fig.tight_layout()
    canvas.draw()

# ---------------- PROGRAM OPERATIONS LOGIC ----------------

def load_medicines():
    medicine_list.delete(0, tk.END)
    medicines = load_json()

    total = len(medicines)
    taken = 0
    missed = 0

    for medicine in medicines:
        status = " 🟡 Pending"
        if medicine.get("taken"):
            status = " ✅ Taken"
            taken += 1
        elif medicine.get("missed"):
            status = " ❌ Missed"
            missed += 1

        name = medicine.get('name', 'Unknown')
        dosage = medicine.get('dosage', 'N/A')
        date = medicine.get('date', 'N/A')
        med_time = medicine.get('time', 'N/A')

        medicine_list.insert(
            tk.END,
            f"  {name:<22} | Units: {dosage:<8} | Date: {date:<12} | Time: {med_time:<8} | {status}"
        )

    pending = total - taken - missed

    total_label.config(text=f"Total: {total}")
    taken_label.config(text=f"Taken: {taken}")
    missed_label.config(text=f"Missed: {missed}")
    pending_label.config(text=f"Pending: {pending}")
    
    root.after_idle(update_graph)

def add_medicine():
    name = medicine_entry.get().strip()
    dosage = dosage_entry.get().strip()
    date = date_entry.get()
    med_time = time_entry.get().strip()

    if not phone_entry.get().strip():
        messagebox.showwarning("Profile Configuration Alert", "Please enter your WhatsApp Phone number first!")
        return

    if not name or not dosage or not med_time:
        messagebox.showwarning("Input Error", "All fields are strictly required!")
        return

    if not re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", med_time):
        messagebox.showwarning("Format Error", "Invalid time! Please use 24hr format HH:MM")
        return

    medicines = load_json()
    medicines.append({
        "name": name,
        "dosage": dosage,
        "date": date,
        "time": med_time,
        "taken": False,
        "missed": False
    })
    
    save_json(medicines)
    clear_fields()
    schedule_all()
    load_medicines()
    messagebox.showinfo("Success", "Medicine logged successfully!")

def search_medicine():
    keyword = search_entry.get().strip().lower()
    medicine_list.delete(0, tk.END)
    medicines = load_json()

    for medicine in medicines:
        name = medicine.get('name', 'Unknown')
        if keyword in name.lower():
            if medicine.get("taken"): status = " ✅ Taken"
            elif medicine.get("missed"): status = " ❌ Missed"
            else: status = " 🟡 Pending"

            dosage = medicine.get('dosage', 'N/A')
            date = medicine.get('date', 'N/A')
            med_time = medicine.get('time', 'N/A')

            medicine_list.insert(
                tk.END,
                f"  {name:<22} | Units: {dosage:<8} | Date: {date:<12} | Time: {med_time:<8} | {status}"
            )

def check_missed_doses():
    now = datetime.now()
    medicines = load_json()
    updated = False

    today = now.strftime("%d/%m/%Y")
    current_time = now.strftime("%H:%M")

    for medicine in medicines:
        med_date = medicine.get("date", "N/A")
        med_time = medicine.get("time", "N/A")

        if med_date != today:
            continue

        if (
            med_time < current_time
            and not medicine.get("taken")
            and not medicine.get("missed")
        ):
            medicine["missed"] = True
            updated = True

    if updated:
        save_json(medicines)
        load_medicines()
        schedule_all()

    root.after(30000, check_missed_doses)

def refresh():
    search_entry.delete(0, tk.END)
    load_medicines()

def mark_taken():
    selected = medicine_list.curselection()
    if not selected:
        messagebox.showwarning("Selection Required", "Please choose a record from the viewer.")
        return

    index = selected[0]
    medicines = load_json()

    if index < len(medicines):
        medicines[index]["taken"] = True
        medicines[index]["missed"] = False

        save_json(medicines)
        load_medicines()
        messagebox.showinfo("Status Update", "Selected log registered successfully.")

def delete_medicine():
    selected = medicine_list.curselection()
    if not selected:
        messagebox.showwarning("Selection Required", "Please choose a target medicine.")
        return

    if not messagebox.askyesno("Confirm Delete", "Permanently purge this entry?"):
        return

    index = selected[0]
    medicines = load_json()
    
    if index < len(medicines):
        medicines.pop(index)
        save_json(medicines)
        load_medicines()
        schedule_all()
        messagebox.showinfo("Success", "Medicine removed.")

def edit_medicine():
    selected = medicine_list.curselection()
    if not selected:
        messagebox.showwarning("Selection Required", "Please choose a record to alter.")
        return

    index = selected[0]
    medicines = load_json()
    
    if index < len(medicines):
        medicine = medicines[index]
        medicine_entry.delete(0, tk.END)
        medicine_entry.insert(0, medicine.get("name", ""))
        dosage_entry.delete(0, tk.END)
        dosage_entry.insert(0, medicine.get("dosage", ""))
        time_entry.delete(0, tk.END)
        time_entry.insert(0, medicine.get("time", ""))
        try:
            date_entry.set_date(datetime.strptime(medicine.get("date", ""), "%d/%m/%Y"))
        except:
            pass

        update_button.index = index
        add_button.config(state=tk.DISABLED)
        update_button.config(state=tk.NORMAL)

def update_medicine():
    index = getattr(update_button, 'index', None)
    if index is None: return

    medicines = load_json()
    if index < len(medicines):
        medicines[index]["name"] = medicine_entry.get().strip()
        medicines[index]["dosage"] = dosage_entry.get().strip()
        medicines[index]["date"] = date_entry.get()
        medicines[index]["time"] = time_entry.get().strip()

        save_json(medicines)
        clear_fields()
        schedule_all()
        load_medicines()
        messagebox.showinfo("Success", "Medicine entry updated successfully.")

def clear_fields():
    medicine_entry.delete(0, tk.END)
    dosage_entry.delete(0, tk.END)
    time_entry.delete(0, tk.END)
    add_button.config(state=tk.NORMAL)
    update_button.config(state=tk.DISABLED)

def validate_time(event=None):
    med_time = time_entry.get().strip()
    if med_time and not re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", med_time):
        messagebox.showwarning("Validation Warning", "Format must match 24-hour HH:MM structure.")

def clear_all():
    if not messagebox.askyesno("Destructive Action", "Flush entire local registry data safely?"): return
    save_json([])
    schedule.clear()
    load_medicines()
    messagebox.showinfo("Purge Processed", "All entries wiped.")

def exit_app():
    if messagebox.askyesno("System Request", "Safely terminate structural processes?"): root.destroy()

# ----------------- ANIMATED HOVER UTILITY -----------------

def bind_button_hover(widget, hover_color, normal_color):
    """Binds mouse events to buttons to create responsive hover animations."""
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_color))

# ---------------- SLATE MAC PREMIUM GRAPHICS BUILD ----------------

root = tk.Tk()
root.title("Executive Scheduler & Retinal Dashboard System")
root.geometry("1480x890")  
root.configure(bg='#0d0d0f')
root.resizable(True, True)

main_layout = tk.Frame(root, bg='#0d0d0f')
main_layout.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

left_panel = tk.Frame(main_layout, bg='#0d0d0f')
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_panel = tk.Frame(main_layout, bd=0, bg='#1a1a1e', padx=14, pady=14)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(24, 0))

title = tk.Label(left_panel, text="Dashboard Workspace", font=("Helvetica Neue", 22, "bold"), fg="#ffffff", bg='#0d0d0f')
title.pack(pady=(0, 16), anchor='w')

# User Settings Container Block (Gmail config removed)
profile_frame = tk.Frame(left_panel, bd=0, bg='#1a1a1e', pady=12, padx=14)
profile_frame.pack(fill=tk.X, pady=6)

tk.Label(profile_frame, text="User Identifier:", font=("Helvetica Neue", 10, "bold"), fg="#8e8e93", bg='#1a1a1e').grid(row=0, column=0, sticky='w')
username_entry = tk.Entry(profile_frame, width=24, font=("Helvetica Neue", 10), bg='#0d0d0f', fg='#ffffff', insertbackground='white', bd=1, relief=tk.FLAT)
username_entry.insert(0, "Patient Admin")
username_entry.grid(row=0, column=1, padx=8, pady=2)

tk.Label(profile_frame, text="Destination Line:", font=("Helvetica Neue", 10, "bold"), fg="#8e8e93", bg='#1a1a1e').grid(row=0, column=2, sticky='w', padx=12)
phone_entry = tk.Entry(profile_frame, width=24, font=("Helvetica Neue", 10), bg='#0d0d0f', fg='#ffffff', insertbackground='white', bd=1, relief=tk.FLAT)
phone_entry.insert(0, "") 
phone_entry.grid(row=0, column=3, padx=8, pady=2)

# Dynamic iOS-Inspired Stat Cards
dashboard = tk.Frame(left_panel, bg='#0d0d0f')
dashboard.pack(pady=16, fill=tk.X)

total_label = tk.Label(dashboard, text="Total: 0", width=14, font=("Helvetica Neue", 11, "bold"), fg="#ffffff", bg='#2c2c2e', padx=8, pady=10)
total_label.grid(row=0, column=0, padx=(0, 8))
taken_label = tk.Label(dashboard, text="Taken: 0", width=14, font=("Helvetica Neue", 11, "bold"), fg="#ffffff", bg='#30d158', padx=8, pady=10)
taken_label.grid(row=0, column=1, padx=8)
pending_label = tk.Label(dashboard, text="Pending: 0", width=14, font=("Helvetica Neue", 11, "bold"), fg="#ffffff", bg='#ffcc00', padx=8, pady=10)
pending_label.grid(row=0, column=2, padx=8)
missed_label = tk.Label(dashboard, text="Missed: 0", width=14, font=("Helvetica Neue", 11, "bold"), fg="#ffffff", bg='#ff453a', padx=8, pady=10)
missed_label.grid(row=0, column=3, padx=8)

# Input Workspace Container Panel
form_frame = tk.Frame(left_panel, bg='#1a1a1e', padx=16, pady=16)
form_frame.pack(fill=tk.X, pady=12)

tk.Label(form_frame, text="Medicine Descriptor Label", font=("Helvetica Neue", 10, "bold"), fg="#aeaeac", bg='#1a1a1e').grid(row=0, column=0, padx=5, pady=6, sticky='w')
medicine_entry = tk.Entry(form_frame, width=38, font=("Helvetica Neue", 11), bg='#0d0d0f', fg='#ffffff', insertbackground='white', bd=0)
medicine_entry.grid(row=0, column=1, padx=12, pady=6)

tk.Label(form_frame, text="Volumetric Dosage Metric", font=("Helvetica Neue", 10, "bold"), fg="#aeaeac", bg='#1a1a1e').grid(row=1, column=0, padx=5, pady=6, sticky='w')
dosage_entry = tk.Entry(form_frame, width=38, font=("Helvetica Neue", 11), bg='#0d0d0f', fg='#ffffff', insertbackground='white', bd=0)
dosage_entry.grid(row=1, column=1, padx=12, pady=6)

tk.Label(form_frame, text="Target Calendar Date", font=("Helvetica Neue", 10, "bold"), fg="#aeaeac", bg='#1a1a1e').grid(row=2, column=0, padx=5, pady=6, sticky='w')
date_entry = DateEntry(form_frame, width=35, font=("Helvetica Neue", 11), date_pattern="dd/mm/yyyy", background='#2c2c2e', foreground='white', headersbackground='#1a1a1e')
date_entry.grid(row=2, column=1, padx=12, pady=6)

tk.Label(form_frame, text="Target Chrono Window (HH:MM)", font=("Helvetica Neue", 10, "bold"), fg="#aeaeac", bg='#1a1a1e').grid(row=3, column=0, padx=5, pady=6, sticky='w')
time_entry = tk.Entry(form_frame, width=38, font=("Helvetica Neue", 11), bg='#0d0d0f', fg='#ffffff', insertbackground='white', bd=0)
time_entry.grid(row=3, column=1, padx=12, pady=6)
time_entry.bind("<FocusOut>", validate_time)

button_frame = tk.Frame(left_panel, bg='#0d0d0f')
button_frame.pack(pady=6, anchor='w')

add_button = tk.Button(button_frame, text="➕ Commit Registry", width=18, bg="#30d158", fg="white", font=("Helvetica Neue", 10, "bold"), bd=0, cursor="hand2")
add_button.config(command=add_medicine)
add_button.grid(row=0, column=0, padx=(0, 12))
bind_button_hover(add_button, "#249e43", "#30d158")

update_button = tk.Button(button_frame, text="💾 Save Modifications", width=20, bg="#ffcc00", fg="black", font=("Helvetica Neue", 10, "bold"), bd=0, state=tk.DISABLED, cursor="hand2")
update_button.config(command=update_medicine)
update_button.grid(row=0, column=1, padx=12)
bind_button_hover(update_button, "#cca300", "#ffcc00")

# Search Filtering Layout
search_frame = tk.Frame(left_panel, bg='#0d0d0f')
search_frame.pack(pady=16, fill=tk.X)

search_entry = tk.Entry(search_frame, width=30, font=("Helvetica Neue", 10), bg='#1a1a1e', fg='#ffffff', insertbackground='white', bd=0)
search_entry.grid(row=0, column=0, padx=(0, 8), ipady=4)

search_btn = tk.Button(search_frame, text="🔍 Query Logs", bg="#2c2c2e", fg="white", font=("Helvetica Neue", 9, "bold"), bd=0, command=search_medicine, padx=12)
search_btn.grid(row=0, column=1, padx=5)
bind_button_hover(search_btn, "#44444a", "#2c2c2e")

reset_btn = tk.Button(search_frame, text="🔄 Flush Views", bg="#2c2c2e", fg="white", font=("Helvetica Neue", 9, "bold"), bd=0, command=refresh, padx=12)
reset_btn.grid(row=0, column=2, padx=5)
bind_button_hover(reset_btn, "#44444a", "#2c2c2e")

# High-Tech Monospaced Listbox Grid Layout
medicine_list = tk.Listbox(left_panel, width=88, height=14, font=("Consolas", 11), bg='#1a1a1e', fg='#eeeeee', bd=0, selectbackground='#30d158', selectforeground='white', highlightthickness=0)
medicine_list.pack(pady=6)

action_frame = tk.Frame(left_panel, bg='#0d0d0f')
action_frame.pack(pady=12, anchor='w')

done_btn = tk.Button(action_frame, text="✔ Terminate Pending", width=18, font=("Helvetica Neue", 10, "bold"), bg="#30d158", fg="white", bd=0, command=mark_taken, cursor="hand2")
done_btn.grid(row=0, column=0, padx=(0, 8))
bind_button_hover(done_btn, "#249e43", "#30d158")

edit_btn = tk.Button(action_frame, text="✏ Alter Config", width=16, font=("Helvetica Neue", 10, "bold"), bg="#2c2c2e", fg="white", bd=0, command=edit_medicine, cursor="hand2")
edit_btn.grid(row=0, column=1, padx=8)
bind_button_hover(edit_btn, "#44444a", "#2c2c2e")

del_btn = tk.Button(action_frame, text="🗑 Purge Record", width=16, bg="#ff453a", fg="white", font=("Helvetica Neue", 10, "bold"), bd=0, command=delete_medicine, cursor="hand2")
del_btn.grid(row=0, column=2, padx=8)
bind_button_hover(del_btn, "#cc2c23", "#ff453a")

last_frame = tk.Frame(left_panel, bg='#0d0d0f')
last_frame.pack(pady=(16, 0), anchor='w')

clear_btn = tk.Button(last_frame, text="🗑 Reset Dataset", width=18, bg="#ff453a", fg="white", font=("Helvetica Neue", 10, "bold"), bd=0, command=clear_all, cursor="hand2")
clear_btn.grid(row=0, column=0, padx=(0, 12))
bind_button_hover(clear_btn, "#cc2c23", "#ff453a")

exit_btn = tk.Button(last_frame, text="❌ Close Application Window", width=25, bg="#2c2c2e", fg="white", font=("Helvetica Neue", 10, "bold"), bd=0, command=exit_app, cursor="hand2")
exit_btn.grid(row=0, column=1, padx=12)
bind_button_hover(exit_btn, "#44444a", "#2c2c2e")

# ---------------- INITIALIZE DYNAMIC GRAPH CANVAS ----------------

fig, ax = plt.subplots(figsize=(6.4, 7.4), dpi=100)
fig.patch.set_facecolor('#1a1a1e')
canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ---------------- RUNTIME INSTANTIATION ----------------

load_medicines()
schedule_all()
check_missed_doses()

root.mainloop()