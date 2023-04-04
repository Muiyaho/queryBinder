import tkinter as tk
from tkinter import scrolledtext
import re
import tkinter.messagebox as messagebox


def bind_query(query_template, params):
    params_list = ["'{}'".format(p.strip()) for p in params.split(',')]
    query_template = re.sub(r'\?', r'{}', query_template)
    return query_template.format(*params_list)


def extract_query_params(log_text):
    param_pattern = r'Parameters: \[(.*?)\]'
    param_match = re.search(param_pattern, log_text)

    params = param_match.group(1) if param_match else ""
    return params


def submit():
    log_text = query_text.get("1.0", tk.END).strip()
    query_template = log_text.split("DEBUG")[0].strip()
    params = extract_query_params(log_text)

    params_label_var.set(f"Parameters ({len(params.split(','))}): {params}")

    result = bind_query(query_template, params)
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, result)
    copy_to_clipboard()


def clear():
    query_text.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)
    params_label_var.set("Parameters (0):")


def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(result_text.get("1.0", tk.END).strip())
    messagebox.showinfo("복사 완료", "복사 완료")


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
params_label.grid(row=2, column=0, sticky="w", pady=(10, 0))

button_frame = tk.Frame(root)
button_frame.grid(row=3, column=0, pady=(10, 0))

submit_button = tk.Button(button_frame, text="Bind", command=submit)
submit_button.pack(side="left")

clear_button = tk.Button(button_frame, text="Clear", command=clear)
clear_button.pack(side="left", padx=(10, 0))

clipboard_button = tk.Button(button_frame, text="Clipboard", command=copy_to_clipboard)
clipboard_button.pack(side="left", padx=(10, 0))

result_label = tk.Label(root, text="Result:")
result_label.grid(row=4, column=0, sticky="w", pady=(10, 0))
result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
result_text.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))

root.mainloop()
