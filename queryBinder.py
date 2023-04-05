import tkinter as tk
from tkinter import scrolledtext, ttk
import re
import tkinter.messagebox as messagebox


def bind_query(query_template, params):
    query_template = re.sub(r'\?', r"'{}'", query_template)
    return query_template.format(*params)


def extract_query_params(log_text):
    param_pattern = r'Parameters: \[(.*?)\]'
    param_match = re.search(param_pattern, log_text)

    params = param_match.group(1).split(',') if param_match else []
    return params


def extract_binding_vars(query_template):
    matches = re.findall(r"(\w+)\s*=\s*\?", query_template)
    question_marks = query_template.count("?")

    while len(matches) < question_marks:
        matches.append("temp")

    return matches


def submit():
    log_text = query_text.get("1.0", tk.END).strip()
    query_template = log_text.split("DEBUG")[0].strip()

    params = extract_query_params(log_text)
    binding_vars = extract_binding_vars(query_template)

    for i, (param, binding_var) in enumerate(zip(params, binding_vars)):
        param_name_labels[i].config(text=f"{binding_var}:")
        param_entries[i].delete(0, tk.END)
        param_entries[i].insert(0, param.strip())

    params_label_var.set(f"Parameters ({len(params)}): {', '.join(params)}")

    result = bind_query(query_template, params)
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, result)

    update_button.grid(row=10, column=0, pady=(10, 0))
    clipboard_button.grid(row=10, column=1, pady=(10, 0))
    update_params()

def clear():
    query_text.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)
    params_label_var.set("Parameters (0):")
    for entry, var_name_label in zip(param_entries, param_name_labels):
        entry.grid_forget()
        var_name_label.grid_forget()
    root.geometry("610x433")

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(result_text.get("1.0", tk.END).strip())
    messagebox.showinfo("복사 완료", "클립보드로 복사 되었습니다.")


def update_params():
    log_text = query_text.get("1.0", tk.END).strip()
    query_template = log_text.split("DEBUG")[0].strip()
    binding_vars = extract_binding_vars(log_text)

    params = []
    for i, binding_var in enumerate(binding_vars):
        param_name_labels[i].config(text=f"{binding_var}:")
        param_entries[i].grid(row=i, column=1)
        param_name_labels[i].grid(row=i, column=0)
        params.append(param_entries[i].get().strip())

    for i in range(len(binding_vars), 100):
        param_entries[i].grid_remove()
        param_name_labels[i].grid_remove()

    for i, (param, binding_var) in enumerate(zip(params, binding_vars)):
        param_name_labels[i].config(text=f"{binding_var}:")
        param_entries[i].delete(0, tk.END)
        param_entries[i].insert(0, param.strip())

    params_label_var.set(f"Parameters ({len(params)}): {', '.join(params)}")

    result = bind_query(query_template, params)
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, result)

    update_button.grid(row=10, column=0, pady=(10, 0))
    root.geometry("611x433")

def update_param_entries():
    update_params()

root = tk.Tk()
root.title("Query Binding")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew")

# Configure rows and columns for dynamic resizing
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)
frame.rowconfigure(2, weight=1)
frame.rowconfigure(3, weight=1)

query_label = tk.Label(frame, text="Log Text:")
query_label.grid(row=0, column=0, sticky="nw", pady=(10, 0))
query_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=10)
query_text.grid(row=1, column=0, sticky="nsew", padx=10)

params_label_var = tk.StringVar()
params_label_var.set("Parameters (0):")
params_label = tk.Label(frame, textvariable=params_label_var)
params_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
params_label.grid_remove()

bind_button = tk.Button(frame, text="Bind", command=submit)
bind_button.grid(row=3, column=0, sticky="w", padx=5, pady=(10, 0))

update_button = tk.Button(frame, text="Update Parameters", command=update_param_entries)
update_button.grid(row=6, column=0, sticky="w",  padx=5, pady=(10, 0))

clipboard_button = tk.Button(frame, text="Copy to Clipboard", command=copy_to_clipboard)
clipboard_button.grid(row=6, column=0, sticky="e",  padx=5, pady=(10, 0))

clear_button = tk.Button(frame, text="Clear", command=clear)
clear_button.grid(row=3, column=0, sticky="e", padx=5, pady=(10, 0))

result_label = tk.Label(frame, text="Result:")
result_label.grid(row=4, column=0, sticky="w", pady=(10, 0))
result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=10)
result_text.grid(row=5, column=0, sticky="nsew", padx=10)

params_frame = tk.Frame(frame)
params_frame.grid(row=1, column=1, rowspan=5, sticky="nsew", padx=(10, 0))

# Adding a canvas for scrolling functionality
params_canvas = tk.Canvas(params_frame, width=200)
params_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Adding a scrollbar
scrollbar = ttk.Scrollbar(params_frame, orient="vertical", command=params_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configuring the canvas
params_canvas.configure(yscrollcommand=scrollbar.set)
params_canvas.bind('<Configure>', lambda e: params_canvas.configure(scrollregion=params_canvas.bbox("all")))

# Adding a frame for the param_entries and param_name_labels
entries_frame = tk.Frame(params_canvas)
params_canvas.create_window((0, 0), window=entries_frame, anchor="nw")

param_entries = [tk.Entry(entries_frame, width=10) for _ in range(100)]
param_name_labels = [tk.Label(entries_frame, text=f"Var {i+1}:") for i in range(100)]

root.mainloop()