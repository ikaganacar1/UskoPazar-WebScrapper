from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from collections import Counter
from sys import argv
from time import sleep
from os import system
import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import platform
import json
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

class Usko:
    def __init__(self):
        try:
            with open("config.json","r") as js:
                conf = json.load(js)
                self.bot_api = conf["config"]["slack_api_key"]
                self.channel_name = conf["config"]["slack_channel_name"]
                self.bot_name = conf["config"]["slack_bot_name"]
                self.update_frequency = conf["config"]["update_frequency"]

        except Exception as e:
            print("Check config.json!  ", e)
            quit()
        
        self.sold_item_list = []
        self.last_updated = ""
        
    def get_sales(self) -> list:
        return self.driver.find_elements(By.CSS_SELECTOR, "[class='flex border-t border-jacarta-100 py-2 px-4 transition-shadow hover:shadow-lg dark:border-jacarta-600 dark:bg-jacarta-900']")

    def get_page(self) -> str:
        return self.driver.page_source
    
    def search_for_user(self):
        
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get("https://www.uskopazar.com/")
        
        dropdown_toggle = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "filtersPrice"))
        )
        dropdown_toggle.click()

        dropdown_menu = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dropdown-menu')]"))
        )

        self.driver.execute_script(
            "arguments[0].setAttribute('class', arguments[0].getAttribute('class').replace('hidden', ''));", 
            dropdown_menu
        )

        zero4_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn_zero4"))
        )
        self.driver.execute_script("arguments[0].click();", zero4_button)

        if self.mode == "buy":
            buy_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "view-list-tab"))
            )
            self.driver.execute_script("arguments[0].click();", buy_button)
        
        search_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "search_useroritem"))
        )
        Select(search_select).select_by_value("1")

        # Add this before your search_input section
        record_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn_top_list"))
        )
        Select(record_dropdown).select_by_value("24")
        
        search_input = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "xsearchInput"))
        )
        search_input.send_keys(self.username)
        
        try:
            search_icon = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[.//svg[contains(@class, 'fill-jacarta-500')]]"))
            )
            search_icon.click()
        except:
            try:
                self.driver.execute_script("document.getElementById('xsearchInput').dispatchEvent(new Event('change'));")
            except:
                search_input.send_keys(Keys.RETURN)
      
    def find_differences(self, list1, list2) -> list:
        return list(Counter(list1) - Counter(list2) )
    
    def take_snapshot(self) -> list:
        item_list = []
        for item in self.get_sales():
            item_list.append(item.find_element(By.CSS_SELECTOR,"[class='text-sm text-jacarta-700 dark:text-white']").text.strip())
        return item_list
         
    def send_notification(self,message):
        client = WebClient(token=self.bot_api)

        try:
            client.chat_postMessage(channel=self.channel_name, text=message,username=self.bot_name)
        except SlackApiError as e:
            print(f"Error sending message: {e}")
         
    def watch_sales(self):
        self.search_for_user()
        initial_snapshot = self.take_snapshot()


        while True:                
            self.watching_listbox.delete(0,tk.END)
            for i in initial_snapshot:
                self.watching_listbox.insert(tk.END, i)                
            
            self.sold_listbox.delete(0,tk.END)              
            for j in self.sold_item_list:
                self.sold_listbox.insert(tk.END, j)
            
            if len(initial_snapshot) == 0:
                self.send_notification("All items Sold!")
                break

            check_snapshot = self.take_snapshot()
            self.last_updated = str(datetime.datetime.now().strftime("%H:%M"))
            self.last_updated_label.config(text=f"Last Updated: {self.last_updated}")
            
            diffirences = self.find_differences(initial_snapshot, check_snapshot)
            if len(diffirences) != 0:
                
                for sold_item in diffirences:
                    self.send_notification(f"{sold_item} sold. {self.last_updated}")
                    self.sold_item_list.append(sold_item)
                
                initial_snapshot = self.take_snapshot()
                
            
            sleep(self.update_frequency)
            self.search_for_user()
            
    def init_gui(self):
        self.root = tk.Tk()
        self.root.title("Usko Market Watcher -ikaganacar")
        self.root.geometry("700x500")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        self.username_label = tk.Label(self.input_frame, text="Enter Username:")
        self.username_label.grid(row=0, column=0, sticky="w", padx=5)
        self.username_entry = tk.Entry(self.input_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5)

        self.mode_label = tk.Label(self.input_frame, text="Select Mode:")
        self.mode_label.grid(row=0, column=2, sticky="w", padx=10)
        self.mode_var = tk.StringVar(value="sell")
        self.mode_sell = ttk.Radiobutton(self.input_frame, text="Sell", variable=self.mode_var, value="sell")
        self.mode_sell.grid(row=0, column=3, sticky="w")
        self.mode_buy = ttk.Radiobutton(self.input_frame, text="Buy", variable=self.mode_var, value="buy")
        self.mode_buy.grid(row=0, column=4, sticky="w")

        self.run_button = tk.Button(self.input_frame, text="Run", command=self.run)
        self.run_button.grid(row=0, column=5, padx=10)

        self.watching_label = tk.Label(self.main_frame, text="Watching Items:")
        self.watching_label.grid(row=1, column=0, sticky="nw", pady=5)
        self.watching_listbox = tk.Listbox(self.main_frame, height=10, width=40)
        self.watching_listbox.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")

        self.sold_label = tk.Label(self.main_frame, text="Sold Items:")
        self.sold_label.grid(row=1, column=1, sticky="nw", pady=5)
        self.sold_listbox = tk.Listbox(self.main_frame, height=10, width=40)
        self.sold_listbox.grid(row=2, column=1, pady=5, padx=5, sticky="nsew")

        self.last_updated_label = tk.Label(self.main_frame, text="Last Updated: N/A")
        self.last_updated_label.grid(row=3, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(self.main_frame, text="Status: Idle", fg="green")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        self.root.mainloop()
        

    def run(self):
        self.username = self.username_entry.get()
        self.mode = self.mode_var.get()

        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty!")
            return

        self.status_label.config(text="Status: Running", fg="blue")

        self.watching_listbox.delete(0, tk.END)

        def start():
            try:
                
                self.search_for_user()

                initial_snapshot = self.take_snapshot()
                if not initial_snapshot:
                    messagebox.showinfo("Info", f"No items to watch for {self.username}.")
                    self.status_label.config(text="Status: Idle", fg="green")
                    return

                self.watch_sales()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.status_label.config(text="Status: Idle", fg="green")

        Thread(target=start, daemon=True).start()


if __name__ == "__main__":
    app = Usko()
    app.init_gui()
