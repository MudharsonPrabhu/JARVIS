import customtkinter as ctk
import datetime
import psutil
import threading
from PIL import Image, ImageTk
from jarvis_main import system_shutdown


class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("JARVIS AI Assistant")
        self.geometry("800x500")

        # Set Background Image
        image_path = "C:/Users/mudha/OneDrive/Desktop/javascript/thumbnail/2.jpg"
        self.bg_image = ctk.CTkImage(light_image=Image.open(image_path), size=(800, 500))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Transparent background on all widgets
        self.title_label = ctk.CTkLabel(self, text="JARVIS Voice Assistant", font=("Arial", 24, "bold"), text_color="white", bg_color="transparent")
        self.title_label.pack(pady=10)

        self.status_text = ctk.CTkTextbox(self, width=700, height=250, font=("Consolas", 14), fg_color="#1E1E1E", text_color="white")
        self.status_text.pack(pady=10)
        self.status_text.insert("0.0", "Status: Awaiting wake word or whistle...\n")
        self.status_text.configure(state="disabled")

        self.time_label = ctk.CTkLabel(self, text="Time: --:--:--", font=("Arial", 16), text_color="white", bg_color="transparent")
        self.time_label.pack()

        self.date_label = ctk.CTkLabel(self, text="Date: ---- -- ----", font=("Arial", 16), text_color="white", bg_color="transparent")
        self.date_label.pack()

        self.battery_label = ctk.CTkLabel(self, text="Battery: --%", font=("Arial", 16), text_color="white", bg_color="transparent")
        self.battery_label.pack(pady=(5, 15))

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(self.button_frame, text="Start Assistant", command=self.start_assistant)
        self.start_button.grid(row=0, column=0, padx=10)

        self.shutdown_button = ctk.CTkButton(self.button_frame, text="Shutdown System", command=self.shutdown_system)
        self.shutdown_button.grid(row=0, column=1, padx=10)

        self.exit_button = ctk.CTkButton(self.button_frame, text="Exit JARVIS", command=self.exit_jarvis)
        self.exit_button.grid(row=0, column=2, padx=10)

        self.update_time_and_battery()

    def update_status(self, text):
        self.status_text.configure(state="normal")
        self.status_text.insert("end", f"{text}\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def update_time_and_battery(self):
        now = datetime.datetime.now()
        self.time_label.configure(text=now.strftime("Time: %I:%M:%S %p"))
        self.date_label.configure(text=now.strftime("Date: %A, %d %B %Y"))

        battery = psutil.sensors_battery()
        if battery:
            plugged = "Charging" if battery.power_plugged else "On Battery"
            self.battery_label.configure(text=f"{plugged}: {battery.percent}%")
        else:
            self.battery_label.configure(text="Battery info unavailable")

        self.after(1000, self.update_time_and_battery)

    def start_assistant(self):
        self.update_status("Starting assistant...")

    def shutdown_system(self):
        self.update_status("System will shut down shortly.")
        system_shutdown()

    def exit_jarvis(self):
        self.destroy()

if __name__ == "__main__":
    app = JarvisGUI()
    app.mainloop()
