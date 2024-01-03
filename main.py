import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import pkg_resources
import pip
import requests
from bs4 import BeautifulSoup
import sys


class PackageManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Package Manager")
        self.root.geometry("600x400")
        self.dark_mode = False

        self.create_widgets()
        self.load_packages()
        self.root.bind("<F5>", self.show_console_log)

    def create_widgets(self):
        # Switch between installed and downloadable packages
        self.switch_var = tk.StringVar(value="installed")
        switch_label = tk.Label(self.root, text="Switch Packages:")
        switch_installed = tk.Radiobutton(self.root, text="Installed", variable=self.switch_var, value="installed", command=self.load_packages)
        switch_downloadable = tk.Radiobutton(self.root, text="Downloadable", variable=self.switch_var, value="downloadable", command=self.load_packages)

        switch_label.grid(row=0, column=0, pady=(10, 5), padx=10, sticky=tk.W)
        switch_installed.grid(row=0, column=1, pady=(10, 5), padx=5)
        switch_downloadable.grid(row=0, column=2, pady=(10, 5), padx=5)

        # Search bar
        self.search_var = tk.StringVar()
        search_label = tk.Label(self.root, text="Search:")
        search_entry = tk.Entry(self.root, textvariable=self.search_var)
        search_button = tk.Button(self.root, text="Search", command=self.load_packages)

        search_label.grid(row=1, column=0, pady=(5, 5), padx=10, sticky=tk.W)
        search_entry.grid(row=1, column=1, pady=(5, 5), padx=5)
        search_button.grid(row=1, column=2, pady=(5, 5), padx=5)

        # Package list
        self.package_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.package_listbox.grid(row=2, column=0, columnspan=3, pady=(5, 5), padx=10, sticky=tk.W + tk.E + tk.N + tk.S)
        self.package_listbox.bind("<ButtonRelease-1>", self.show_install_button)

        # Install button
        self.install_button = tk.Button(self.root, text="Install", state=tk.DISABLED, command=self.install_package)
        self.install_button.grid(row=3, column=0, columnspan=3, pady=(5, 10), padx=10)

        # Console log
        self.console_log = tk.Text(self.root, height=5, state=tk.DISABLED, wrap=tk.WORD)
        self.console_log.grid(row=4, column=0, columnspan=3, pady=(0, 10), padx=10, sticky=tk.W + tk.E + tk.N + tk.S)

    def load_packages(self):
        self.package_listbox.delete(0, tk.END)
        search_query = self.search_var.get().lower()

        if self.switch_var.get() == "installed":
            packages = [pkg.project_name for pkg in pkg_resources.working_set]
        else:
            if not search_query:
                messagebox.showwarning("Search Warning", "Please enter a search query for downloadable packages.")
                return

            pypi_url = "https://pypi.org/simple/"
            response = requests.get(pypi_url)
            soup = BeautifulSoup(response.content, "html.parser")
            package_elements = soup.find_all("a", href=True)

            packages = [pkg.text for pkg in package_elements if search_query in pkg.text.lower()]

        for package in packages:
            self.package_listbox.insert(tk.END, package)

    def show_install_button(self, event):
        selected_package = self.package_listbox.get(tk.ACTIVE)
        if selected_package:
            self.install_button["state"] = tk.NORMAL
        else:
            self.install_button["state"] = tk.DISABLED

    def install_package(self):
        selected_package = self.package_listbox.get(tk.ACTIVE)
        if selected_package:
            try:
                # Run pip install command and capture the output
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', selected_package],
                                        capture_output=True, text=True, check=True)

                # Display the installation output in the console log
                self.console_log.config(state=tk.NORMAL)
                self.console_log.delete(1.0, tk.END)
                self.console_log.insert(tk.END, result.stdout)
                self.console_log.insert(tk.END, result.stderr)
                self.console_log.config(state=tk.DISABLED)

                messagebox.showinfo("Installation Successful", f"{selected_package} has been successfully installed.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Installation Error", f"An error occurred during the installation of {selected_package}:\n{e}")
            self.install_button["state"] = tk.DISABLED

    def show_console_log(self, event):
        self.console_log.config(state=tk.NORMAL)
        self.console_log.delete(1.0, tk.END)
        self.console_log.insert(tk.END, "Console log will appear here when F5 is pressed.")
        self.console_log.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PackageManagerApp(root)
    root.mainloop()
