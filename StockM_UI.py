import json
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import Envoi_mail


def save_treeview_to_json(tree, filename):
    data = []
    for item in tree.get_children():
        values = tree.item(item)['values']
        data.append(values)

    with open(filename, 'w') as f:
        json.dump(data, f)


class StockUI(tk.Tk):
    ICON = "Logo_GB_2015.ico"
    TREE_SAVE = "tree_save.json"

    def __init__(self):
        super().__init__()
        self.title("Gestion des stocks Amiéditions")
        self.iconbitmap(StockUI.ICON)
        self.style = ttk.Style(self)
        self.tk.call("source", "theme/forest-light.tcl")
        self.style.theme_use("forest-light")
        self.headers = ("Nom", "Modèle", "Référence", "Quantité restante", "Seuil")
        self.menu = self.menu_init()
        self.config(menu=self.menu)
        self.main_frame = self.main_frame_init()
        self.main_tree = self.main_tree_init(self.main_frame)
        self.modif_frame = None

    def menu_init(self):
        menu = tk.Menu(self)
        submenu1 = tk.Menu(menu, tearoff=0)
        submenu2 = tk.Menu(menu, tearoff=0)
        submenu1.add_command(label="Ajouter une référence", command=lambda: self.add_reference())
        submenu1.add_separator()
        submenu1.add_command(label="Quitter", command=lambda: self.destroy())
        submenu2.add_command(label="Email alerte", command=lambda: self.toplevel_email_config())
        menu.add_cascade(label="Fichier", menu=submenu1)
        menu.add_cascade(label="Paramètres", menu=submenu2)
        return menu

    def main_frame_init(self):
        frame = ttk.Frame(self, padding=10)
        title = ttk.Label(frame, text="Gestion des stocks Amiédition", font=("", 14, "bold"))
        title.pack()
        frame.pack()
        return frame

    def main_tree_init(self, frame):
        tree = ttk.Treeview(frame, columns=self.headers, show="headings", selectmode="browse",
                            padding=10, displaycolumns=(0, 1, 2, 3))
        for header in self.headers:
            tree.heading(header, text=f"{header}")
        tree.column(self.headers[0], width=250)
        tree.column(self.headers[1], width=75, anchor="center")
        tree.column(self.headers[2], width=100)
        tree.column(self.headers[3], width=100, anchor="center")
        with open(StockUI.TREE_SAVE) as reference:
            reference_dict = json.load(reference)
        for reference in reference_dict:
            tree.insert('', tk.END, values=reference)
        tree.configure(height=len(reference_dict))
        tree.bind('<<TreeviewSelect>>', lambda event: self.modif_stock_reference(tree))
        tree.pack()
        return tree

    def modif_stock_reference(self, tree):
        selected_item = tree.selection()
        item = tree.set(selected_item, self.headers[0])
        if isinstance(self.modif_frame, ttk.Frame):
            self.modif_frame.destroy()
        if item != "":
            self.modif_frame = ttk.Frame(self, padding=10)
            modif_labelframe = ttk.Labelframe(self.modif_frame, text=f"Mise à jour du stock de {item}", padding=10)
            modif_labelframe.grid(row=0)
            modif_entry = ttk.Spinbox(modif_labelframe, from_=0, to=100, justify="center")
            modif_entry.set(tree.set(selected_item, self.headers[3]))
            modif_entry.grid(row=1, column=0, sticky=tk.E)
            apply_modif_sotck_button = ttk.Button(modif_labelframe, text="Valider", padding=5,
                                                  command=lambda: self.modif_stock_reference_apply(tree, modif_entry,
                                                                                                   selected_item,
                                                                                                   self.modif_frame))
            apply_modif_sotck_button.grid(row=1, column=1, sticky=tk.E)
            cancel_modif_stock_button = ttk.Button(modif_labelframe, text="Annuler", padding=5,
                                                   command=lambda: self.modif_frame.destroy())
            cancel_modif_stock_button.grid(row=1, column=2, sticky=tk.W)
            modif_subframe = ttk.Frame(self.modif_frame, padding=10)
            delete_reference_button = ttk.Button(modif_subframe, text="Supprimer la référence",
                                                 command=lambda: self.delete_reference(tree, selected_item,
                                                                                       self.modif_frame))
            delete_reference_button.grid(row=0, column=1)
            modif_reference_button = ttk.Button(modif_subframe, text="Modifier la référence",
                                                command=lambda: self.modif_reference(tree, selected_item, ))
            modif_reference_button.grid(row=0, column=0)
            modif_subframe.grid(row=1, column=0, columnspan=3)
            self.modif_frame.pack()

    def modif_stock_reference_apply(self, tree, modif_entry, selected_item, modif_frame):
        modif_entry_get = modif_entry.get()
        try:
            int(modif_entry_get)
            tree.set(selected_item, self.headers[3], modif_entry_get)
            save_treeview_to_json(tree, StockUI.TREE_SAVE)
            modif_frame.destroy()
        except ValueError:
            modif_entry.set("")
            messagebox.showwarning(title="ValueError", message="Merci de renseigner une valeur numérique entière")

    def modif_reference(self, tree, selected_item):
        modif_reference_window = tk.Toplevel(self)
        modif_reference_window.iconbitmap(StockUI.ICON)
        modif_reference_window.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty()))
        modif_reference_frame = ttk.LabelFrame(modif_reference_window, text="Modification d'une référence")
        info_entry_list = []
        for index, info in enumerate(tree.set(selected_item)):
            if info != self.headers[3]:
                info_label = ttk.Label(modif_reference_frame, text=info)
                info_entry = ttk.Entry(modif_reference_frame)
                info_entry.insert(0, tree.set(selected_item, self.headers[index]))
                info_label.grid(row=index, column=0)
                info_entry.grid(row=index, column=1)
                info_entry_list.append(info_entry)
        modif_reference_frame.pack()
        add_button = ttk.Button(modif_reference_frame, text="Modifier",
                                command=lambda: self.modif_reference_apply(modif_reference_window,
                                                                           selected_item, *info_entry_list))
        add_button.grid(column=0, columnspan=2)

    def modif_reference_apply(self, modif_reference_window, selected_item, *args):
        values = [arg.get() for arg in args]
        values.insert(3, self.main_tree.item(selected_item)["values"][3])
        erreur_message = ""
        try:
            int(values[4])
        except ValueError:
            values[4] = 0
            erreur_message = " (Attention 'Seuil' mis à 0)"
        for index, header in enumerate(self.headers):
            self.main_tree.set(selected_item, header, values[index])
        save_treeview_to_json(self.main_tree, StockUI.TREE_SAVE)
        modif_reference_window.destroy()
        messagebox.showinfo(title="Modification effectuée", message=f"{values[0]} modifié{erreur_message}")

    def delete_reference(self, tree, selected_item, modif_frame):
        item = tree.set(selected_item, self.headers[0])
        choice = messagebox.askyesno(title="Supprimer référence",
                                     message=f"Voulez vous supprimer la référence {item} ?")
        if choice:
            tree.delete(selected_item)
            save_treeview_to_json(tree, StockUI.TREE_SAVE)
            tree.configure(height=len(tree.get_children()))
            modif_frame.destroy()
            messagebox.showinfo(message="Suppression effectuée")

    def add_reference(self):
        window_reference = tk.Toplevel()
        window_reference.title("Gestion des références")
        window_reference.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty()))
        window_reference.iconbitmap(StockUI.ICON)
        frame_reference = ttk.Frame(window_reference)
        header_entry_list = []
        for index, header in enumerate(self.headers):
            header_label = ttk.Label(frame_reference, text=header)
            header_entry = ttk.Entry(frame_reference)
            header_label.grid(row=index, column=1)
            header_entry.grid(row=index, column=2)
            header_entry_list.append(header_entry)
        frame_reference.pack()
        add_button = ttk.Button(window_reference, text="Ajouter",
                                command=lambda: self.add_reference_apply(window_reference, *header_entry_list))
        add_button.pack()

    def add_reference_apply(self, window_reference, *args):
        values = [arg.get() for arg in args]
        erreur_message = ""
        try:
            int(values[3])
        except ValueError:
            values[3] = 0
            erreur_message = " (Attention 'Quantité restante' mise à 0)"
        self.main_tree.insert('', 'end', values=values)
        self.main_tree.configure(height=len(self.main_tree.get_children()))
        save_treeview_to_json(self.main_tree, StockUI.TREE_SAVE)
        window_reference.destroy()
        messagebox.showinfo(message=f"Référence ajouté{erreur_message}")

    def toplevel_email_config(self):
        email_config = tk.Toplevel()
        email_config.iconbitmap(StockUI.ICON)
        email_config.geometry("650x200+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty()))
        frame_conn_serv = ttk.LabelFrame(email_config, text="Connexion au serveur mail")
        frame_conn_serv.pack(expand=True)
        email_conn_label = ttk.Label(frame_conn_serv, text="Adresse mail : ")
        email_conn_label.grid(row=0, column=0)
        email_conn_entry = ttk.Entry(frame_conn_serv)
        email_conn_entry.grid(row=0, column=1)
        password_conn_label = ttk.Label(frame_conn_serv, text="Mot de passe : ")
        password_conn_label.grid(row=0, column=2)
        password_conn_entry = ttk.Entry(frame_conn_serv, show="●")
        password_conn_entry.grid(row=0, column=3)
        conn_button = ttk.Button(frame_conn_serv, text="Connexion", padding=5)
        conn_button.grid(row=1, column=0, columnspan=4, pady=10)


if __name__ == "__main__":
    root = StockUI()
    root.mainloop()
