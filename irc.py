import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from queue import Queue, Empty
import time

class IRCConnection(threading.Thread):
    """
    Verwaltet eine einzelne IRC-Verbindung inklusive Empfangs-Thread.
    """
    def __init__(self, server, port, channel, nickname, message_queue, identity_label):
        super().__init__(daemon=True)
        self.server = server
        self.port = port
        self.channel = channel
        self.nickname = nickname
        self.message_queue = message_queue
        self.identity_label = identity_label
        self.sock = None
        self.running = False

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(15)
            self.sock.connect((self.server, self.port))
            self.running = True

            self._send_raw(f"NICK {self.nickname}")
            self._send_raw(f"USER {self.nickname} 0 * :Anonymous IRC Client")

            self.message_queue.put((self.identity_label,
                                    f"[System] Verbunden als {self.nickname} @ {self.server}:{self.port}"))

            time.sleep(2)
            self._send_raw(f"JOIN {self.channel}")
            self.message_queue.put((self.identity_label,
                                    f"[System] Channel betreten: {self.channel}"))

            buffer = ""
            while self.running:
                try:
                    data = self.sock.recv(4096)
                    if not data:
                        break
                    buffer += data.decode("utf-8", errors="ignore")
                    while "\r\n" in buffer:
                        line, buffer = buffer.split("\r\n", 1)
                        self._handle_line(line)
                except socket.timeout:
                    continue
                except OSError:
                    break

        except Exception as e:
            self.message_queue.put((self.identity_label,
                                    f"[Fehler] Verbindung fehlgeschlagen ({self.nickname}): {e}"))
        finally:
            self.running = False
            if self.sock:
                try:
                    self.sock.close()
                except OSError:
                    pass
            self.message_queue.put((self.identity_label,
                                    f"[System] Verbindung für {self.nickname} wurde getrennt."))

    def _handle_line(self, line: str):
        line = line.strip()
        if not line:
            return

        if line.startswith("PING"):
            pong_target = line.split(":", 1)[1] if ":" in line else ""
            self._send_raw(f"PONG :{pong_target}")
            return

        display = self._parse_irc_line(line)
        self.message_queue.put((self.identity_label, display))

    def _parse_irc_line(self, raw: str) -> str:
        """
        Parsen einer IRC-Zeile für menschlich lesbare Darstellung.
        """
        prefix = ""
        command = ""
        params = []

        s = raw
        if s.startswith(":"):
            prefix, s = s[1:].split(" ", 1)
        if " " in s:
            command, s = s.split(" ", 1)
            s = s.lstrip()
        else:
            command = s
            s = ""

        while s:
            if s.startswith(":"):
                params.append(s[1:])
                break
            if " " in s:
                p, s = s.split(" ", 1)
                params.append(p)
                s = s.lstrip()
            else:
                params.append(s)
                break

        if command == "PRIVMSG" and len(params) >= 2:
            target = params[0]
            msg = params[1]
            nick = prefix.split("!")[0] if "!" in prefix else prefix
            timestamp = time.strftime("%H:%M:%S")
            return f"[{timestamp}] <{nick}> {msg}"

        if command == "JOIN" and params:
            nick = prefix.split("!")[0] if "!" in prefix else prefix
            ch = params[0]
            timestamp = time.strftime("%H:%M:%S")
            return f"[{timestamp}] *** {nick} hat {ch} betreten"

        if command in ("PART", "QUIT"):
            nick = prefix.split("!")[0] if "!" in prefix else prefix
            timestamp = time.strftime("%H:%M:%S")
            return f"[{timestamp}] *** {nick} hat den Channel verlassen"

        return raw

    def _send_raw(self, line: str):
        if self.sock and self.running:
            try:
                self.sock.sendall((line + "\r\n").encode("utf-8", errors="ignore"))
            except OSError:
                self.running = False

    def send_message(self, channel: str, message: str):
        if not self.running:
            return
        self._send_raw(f"PRIVMSG {channel} :{message}")

    def stop(self):
        self.running = False
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

class AnonymousIRCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anonymous IRC Console — Dual Identity Client")
        self.root.geometry("950x600")
        self.root.configure(bg="#101010")

        self.root.minsize(900, 550)

        self._configure_styles()

        self.conn1 = None
        self.conn2 = None

        self.message_queue = Queue()

        self.active_identity = tk.StringVar(value="id1")

        self._build_header()
        self._build_connection_panel()
        self._build_chat_panel()
        self._build_input_panel()

        self._poll_messages()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "TFrame",
            background="#101010",
        )
        style.configure(
            "Header.TLabel",
            background="#101010",
            foreground="#00ff88",
            font=("Segoe UI", 18, "bold")
        )
        style.configure(
            "SubHeader.TLabel",
            background="#101010",
            foreground="#cccccc",
            font=("Segoe UI", 9)
        )
        style.configure(
            "TLabel",
            background="#101010",
            foreground="#f0f0f0",
            font=("Segoe UI", 9)
        )
        style.configure(
            "Dark.TEntry",
            fieldbackground="#181818",
            foreground="#f0f0f0"
        )
        style.map(
            "Dark.TEntry",
            fieldbackground=[("active", "#202020"), ("focus", "#202020")],
        )

        style.configure(
            "Accent.TButton",
            background="#00b894",
            foreground="#101010",
            font=("Segoe UI Semibold", 9),
            padding=5
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#00d1a0"), ("pressed", "#009f7d")]
        )

    def _build_header(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(10, 4))

        icon_label = ttk.Label(
            header_frame,
            text="☣",
            style="Header.TLabel",
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        title_label = ttk.Label(
            header_frame,
            text="ANONYMOUS IRC CONSOLE",
            style="Header.TLabel",
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(
            header_frame,
            text="Secure Dual-Identity IRC Operator · ©SKIDR0W",
            style="SubHeader.TLabel",
        )
        subtitle_label.pack(side=tk.RIGHT)

    def _build_connection_panel(self):
        conn_frame = ttk.Frame(self.root)
        conn_frame.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(4, 8))

        server_label = ttk.Label(conn_frame, text="Server:")
        server_label.grid(row=0, column=0, sticky="w")
        self.server_entry = ttk.Entry(conn_frame, width=25)
        self.server_entry.grid(row=0, column=1, padx=(2, 10))
        self.server_entry.insert(0, "irc.libera.chat")

        port_label = ttk.Label(conn_frame, text="Port:")
        port_label.grid(row=0, column=2, sticky="w")
        self.port_entry = ttk.Entry(conn_frame, width=6)
        self.port_entry.grid(row=0, column=3, padx=(2, 10))
        self.port_entry.insert(0, "6667")

        channel_label = ttk.Label(conn_frame, text="Channel:")
        channel_label.grid(row=0, column=4, sticky="w")
        self.channel_entry = ttk.Entry(conn_frame, width=20)
        self.channel_entry.grid(row=0, column=5, padx=(2, 10))
        self.channel_entry.insert(0, "#anonymous-chat")

        nick1_label = ttk.Label(conn_frame, text="Nickname #1:")
        nick1_label.grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.nick1_entry = ttk.Entry(conn_frame, width=20)
        self.nick1_entry.grid(row=1, column=1, padx=(2, 10), pady=(6, 0))
        self.nick1_entry.insert(0, "AnonOperator1")

        nick2_label = ttk.Label(conn_frame, text="Nickname #2:")
        nick2_label.grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.nick2_entry = ttk.Entry(conn_frame, width=20)
        self.nick2_entry.grid(row=1, column=3, padx=(2, 10), pady=(6, 0))
        self.nick2_entry.insert(0, "AnonOperator2")

        self.connect_button = ttk.Button(
            conn_frame,
            text="Verbinden (Dual Identity)",
            style="Accent.TButton",
            command=self.connect
        )
        self.connect_button.grid(row=0, column=6, rowspan=2, padx=(10, 0), sticky="nsew")

        self.disconnect_button = ttk.Button(
            conn_frame,
            text="Trennen",
            command=self.disconnect,
        )
        self.disconnect_button.grid(row=0, column=7, rowspan=2, padx=(6, 0), sticky="nsew")

        for i in range(0, 8):
            conn_frame.columnconfigure(i, weight=0)
        conn_frame.columnconfigure(5, weight=1)
        conn_frame.columnconfigure(6, weight=0)
        conn_frame.columnconfigure(7, weight=0)

    def _build_chat_panel(self):
        chat_frame = ttk.Frame(self.root)
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        self.chat_text = tk.Text(
            chat_frame,
            bg="#121212",
            fg="#f0f0f0",
            insertbackground="#f0f0f0",
            font=("Consolas", 10),
            wrap="word",
            state="disabled",
            relief=tk.FLAT,
        )
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_text.tag_configure("id1", foreground="#00ff88")
        self.chat_text.tag_configure("id2", foreground="#00b0ff")
        self.chat_text.tag_configure("system", foreground="#aaaaaa", underline=False)

        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.configure(yscrollcommand=scrollbar.set)

    def _build_input_panel(self):
        input_frame = ttk.Frame(self.root)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=(0, 10))

        id_label = ttk.Label(input_frame, text="Sende als:")
        id_label.grid(row=0, column=0, sticky="w")

        self.id1_radio = ttk.Radiobutton(
            input_frame,
            text="ID #1",
            value="id1",
            variable=self.active_identity
        )
        self.id1_radio.grid(row=0, column=1, padx=(4, 10))

        self.id2_radio = ttk.Radiobutton(
            input_frame,
            text="ID #2",
            value="id2",
            variable=self.active_identity
        )
        self.id2_radio.grid(row=0, column=2, padx=(0, 10))

        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.grid(row=0, column=3, padx=(4, 10), sticky="ew")
        self.message_entry.bind("<Return>", self._on_enter_pressed)

        self.send_button = ttk.Button(
            input_frame,
            text="Senden",
            style="Accent.TButton",
            command=self.send_message
        )
        self.send_button.grid(row=0, column=4, sticky="e")

        input_frame.columnconfigure(3, weight=1)

    def _poll_messages(self):
        """
        Holt Nachrichten aus der Queue und schreibt sie ins Chatfenster.
        """
        try:
            while True:
                identity_label, text = self.message_queue.get_nowait()
                self._append_chat(identity_label, text)
        except Empty:
            pass

        self.root.after(100, self._poll_messages)

    def _append_chat(self, identity_label: str, text: str):
        """
        Fügt eine Zeile in den Chat ein, mit Tagging nach Identity.
        identity_label: "ID#1", "ID#2" oder ähnliches.
        """
        self.chat_text.configure(state="normal")

        at_end = self.chat_text.yview()[1] >= 0.999

        tag = "system"
        if identity_label.upper().startswith("ID#1"):
            tag = "id1"
        elif identity_label.upper().startswith("ID#2"):
            tag = "id2"

        self.chat_text.insert("end", f"[{identity_label}] {text}\n", tag)

        if at_end:
            self.chat_text.see("end")

        self.chat_text.configure(state="disabled")

    def connect(self):
        if self.conn1 or self.conn2:
            messagebox.showinfo("Information", "Bereits verbunden. Bitte zuerst trennen.")
            return

        server = self.server_entry.get().strip()
        channel = self.channel_entry.get().strip()
        port_text = self.port_entry.get().strip()
        nick1 = self.nick1_entry.get().strip()
        nick2 = self.nick2_entry.get().strip()

        if not server or not channel or not port_text:
            messagebox.showerror("Fehler", "Bitte Server, Port und Channel ausfüllen.")
            return

        try:
            port = int(port_text)
        except ValueError:
            messagebox.showerror("Fehler", "Port muss eine Zahl sein.")
            return

        if not nick1 and not nick2:
            messagebox.showerror("Fehler", "Mindestens ein Nickname muss gesetzt sein.")
            return

        self._append_chat("SYSTEM", f"Verbinde zu {server}:{port} / {channel} ...")

        if nick1:
            self.conn1 = IRCConnection(server, port, channel, nick1, self.message_queue, "ID#1")
            self.conn1.start()

        if nick2:
            self.conn2 = IRCConnection(server, port, channel, nick2, self.message_queue, "ID#2")
            self.conn2.start()

    def disconnect(self):
        if self.conn1:
            self.conn1.stop()
            self.conn1 = None
        if self.conn2:
            self.conn2.stop()
            self.conn2 = None

        self._append_chat("SYSTEM", "Verbindungen werden getrennt ...")

    def send_message(self):
        msg = self.message_entry.get().strip()
        if not msg:
            return

        channel = self.channel_entry.get().strip()
        active = self.active_identity.get()

        if active == "id1" and self.conn1 and self.conn1.running:
            self.conn1.send_message(channel, msg)
        elif active == "id2" and self.conn2 and self.conn2.running:
            self.conn2.send_message(channel, msg)
        else:
            messagebox.showwarning(
                "Nicht verbunden",
                f"Die aktuell ausgewählte Identität ({active}) ist nicht verbunden."
            )
            return

        timestamp = time.strftime("%H:%M:%S")
        label = "ID#1" if active == "id1" else "ID#2"
        self._append_chat(label, f"[{timestamp}] (Du) {msg}")

        self.message_entry.delete(0, tk.END)

    def _on_enter_pressed(self, event):
        self.send_message()

    def on_close(self):
        self.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnonymousIRCApp(root)
    root.mainloop()