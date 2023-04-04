import tkinter as tk
from tkinter import scrolledtext, ttk
import re
import tkinter.messagebox as messagebox


def bind_query(query_template, params):
    query_template = re.sub(r'\?', r"'{}'", query_template)
    try:
        return query_template.format(*params)
    except IndexError:
        return "Error: Parameter count mismatch in the query template."


def extract_query_params(log_text):
    param_pattern = r'Parameters: \[(.*?)\]'
    param_match = re.search(param_pattern, log_text)

    params = param_match.group(1).split(',') if param_match else []
    return params


def extract_binding_vars(query_template):
    matches = re.findall(r"(\w+)\s*=\s*\?", query_template)
    return matches


def submit():
    log_text = query_text.get("1.0", tk.END).strip()
    query_template = log_text.split("DEBUG")[0].strip()

    params = extract_query_params(log_text)
    binding_vars = extract_binding_vars(query_template)

    # Check if the number of ? matches the number of parameters
    if query_template.count("?") != len(params):
        messagebox.showwarning("Warning", "Parameter count mismatch in the query template.")
        return

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
    update_param_entries()


def clear():
    query_text.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)
    params_label_var.set("Parameters (0):")
    for entry, var_name_label in zip(param_entries, param_name_labels):
        entry.grid_forget()
        var_name_label.grid_forget()


def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(result_text.get("1.0", tk.END).strip())
    messagebox.showinfo("복사 완료", "클립보드로 복사 되었습니다.")


def update_param_entries():
    log_text = query_text.get("1.0", tk.END).strip()
    query_template = log_text.split("DEBUG")[0].strip()
    binding_vars = extract_binding_vars(log_text)

    params = []
    for i, binding_var in enumerate(binding_vars):
        param_name_labels[i].config(text=f"{binding_var}:")
        param_entries[i].grid(row=i, column=1)
        param_name_labels[i].grid(row=i, column=0)
        params.append(param_entries[i].get().strip())

    for i in range(len(binding_vars), 10):
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
    clipboard_button.grid(row=10, column=1, pady=(10, 0))


root = tk.Tk()
root.title("Query Binding")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

query_label = tk.Label(root, text="Log Text:")
query_label.grid(row=0, column=0, sticky="nw", pady=(10, 0))
query_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
query_text.grid(row=1, column=0, sticky="nsew", padx=10)

params_label_var = tk.StringVar()
params_label_var.set("Parameters (0):")
params_label = tk.Label(root, textvariable=params_label_var)
params_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))

bind_button = tk.Button(root, text="Bind", command=submit)
bind_button.grid(row=3, column=0, sticky="w", padx=10, pady=(10, 0))

clear_button = tk.Button(root, text="Clear", command=clear)
clear_button.grid(row=3, column=0, sticky="e", padx=10, pady=(10, 0))

result_label = tk.Label(root, text="Result:")
result_label.grid(row=4, column=0, sticky="w", pady=(10, 0))
result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
result_text.grid(row=5, column=0, sticky="nsew", padx=10)

params_frame = tk.Frame(root)
params_frame.grid(row=1, column=1, rowspan=5, sticky="nsew", padx=(10, 0))

param_entries = [tk.Entry(params_frame, width=10) for _ in range(10)]
param_name_labels = [tk.Label(params_frame, text=f"Var {i+1}:") for i in range(10)]

update_button = tk.Button(params_frame, text="Update Parameters", command=update_param_entries)
update_button.grid(row=10, column=0, pady=(10, 0))

clipboard_button = tk.Button(params_frame, text="Copy to Clipboard", command=copy_to_clipboard)
clipboard_button.grid(row=10, column=1, pady=(10, 0))

root.mainloop()

