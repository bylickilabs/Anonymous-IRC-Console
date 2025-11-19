
### 🕶️ Anonymous IRC Console — Dual Identity Operator Client (DE/EN README)

> Ein sicheres, plattformübergreifendes IRC-Kommunikationstool für Analysten, Operatoren und Sicherheitsforscher.
  - Diese Anwendung ermöglicht zwei gleichzeitige IRC-Identitäten in einer einzigen Oberfläche 
    – für verdeckte Operationen, Echtzeit-Überwachung und sichere Kommunikation.

<br>

---

<br>

## DE

### 🧩 **Überblick**

Die *Anonymous IRC Console* bietet eine professionelle Mehridentitätsumgebung für IRC.  
- Sie wurde entwickelt, um mehrere IRC-Instanzen gleichzeitig zu steuern, Nachrichten sicher zu verarbeiten und die Kommunikation effizient zu gestalten.

### 🔥 **Hauptfunktionen**
- **Dual Identity Mode:** Zwei Nicknames gleichzeitig aktiv (unabhängige Threads)
- **Echtzeit IRC-Parsing:** Farbcodierte Nachrichten mit Zeitstempeln
- **Ping/Pong-Mechanismus:** Automatische Verbindungserhaltung
- **Thread-sichere Kommunikation:** Keine Race-Conditions
- **Zero-Dependency Architektur:** Nur Python Standardbibliothek
- **Cross-Plattform:** Windows, Linux, macOS
- **GUI:** Moderne, dunkle Oberfläche mit Tkinter und ttk Styles

### 🏗️ **Architekturübersicht**

```yarn
GUI Layer (Tkinter)
 ├── IRCConnection (Thread #1 / ID#1)
 ├── IRCConnection (Thread #2 / ID#2)
 │     ↓
 │   Socket Layer (Async I/O)
 │     ↓
 └── IRC Protocol Handler & Message Queue
```

<br>

---

<br>

### ⚙️ **Installation**
1. **Python 3.10+** installieren  
2. Repository oder Datei `irc.py` herunterladen  
3. Anwendung starten:

```bash
python irc.py
```

### 💬 **Verwendung**

1. Server, Port und Channel eintragen (z. B. `irc.libera.chat`, Port `6667`, `#anonymous-chat`)
2. Zwei Nicknames definieren (z. B. `AnonOperator1`, `AnonOperator2`)
3. „Verbinden (Dual Identity)“ klicken
4. Nachrichten über den unteren Eingabebereich senden

---

### 🧠 **Technische Details**
- **IRCConnection-Klasse:** Baut und verwaltet Socket-Verbindungen, verarbeitet IRC-Kommandos (`PING`, `JOIN`, `PRIVMSG` etc.)
- **MessageQueue:** Synchronisiert Chat-Events zwischen Threads und GUI
- **Thread Safety:** Jeder IRC-Client läuft unabhängig im eigenen Thread

---

### ⚠️ **Sicherheits- und Compliance-Hinweis**
Dieses Tool darf ausschließlich zu Forschungs-, Test- oder Demonstrationszwecken verwendet werden.  
Verbindungen zu öffentlichen IRC-Servern erfolgen auf eigenes Risiko.  
BYLICKILABS übernimmt keine Haftung für unautorisierte Nutzung.

<br>

---

<br>

## EN

### 🧩 **Overview**
> The *Anonymous IRC Console* is a secure dual-identity communication client for IRC analysts and operators.  
  - It allows two simultaneous connections under different nicknames with full control, color-coded real-time output, and zero external dependencies.

### 🔥 **Key Capabilities**
- **Dual Identity Mode:** Operate two nicknames in parallel  
- **Real-Time IRC Parser:** Human-readable IRC message rendering  
- **Automatic PING/PONG:** Keeps both connections alive  
- **Thread-Safe Architecture:** Reliable multi-thread message handling  
- **No External Dependencies:** Fully Python standard library  
- **Modern UI:** Dark interface with Tkinter-based layout  
- **Cross-Platform:** Runs on Windows, Linux, and macOS  

### 🏗️ **Software Architecture**

```yarn
GUI Layer (Tkinter)
 ├── IRCConnection (Thread #1 / ID#1)
 ├── IRCConnection (Thread #2 / ID#2)
 │     ↓
 │   Socket Layer (Async I/O)
 │     ↓
 └── IRC Protocol Handler & Message Queue
```

<br>

---

<br>

### ⚙️ **Setup**
1. Install **Python 3.10+**
2. Download or clone the repository containing `irc.py`
3. Run the application:

```bash
python irc.py
```

<br>

---

<br>

### 💬 **Usage**

1. Enter IRC **server**, **port**, and **channel**
2. Set two **nicknames** (e.g., `AnonOperator1` and `AnonOperator2`)
3. Press **Connect (Dual Identity)**
4. Use the lower input field to send messages as either identity

---

### 🧠 **Technical Insight**

---

- The **IRCConnection** class manages socket connections, message parsing, and event routing.  
- The **Queue** ensures thread-safe interaction between IRC threads and GUI.  
- **Color-coding** helps distinguish messages by identity (green for ID#1, blue for ID#2).

---

### 🔒 **Security Notice**

This software is intended solely for educational and ethical research purposes.  
Unauthorized use on external systems is prohibited.  
Use responsibly within your organization’s security policies.

<br>

---

<br>

## 🧾 **Projectinformation**

**Name:** Anonymous IRC Console  
**Version:** 1.0.0  
**Entwickler:** ©Thorsten Bylicki | ©BYLICKILABS  
**Lizenz:** MIT License  
**Sprache:** Python 3.x  
**GUI:** Tkinter  
**Zielplattformen:** Windows / Linux / macOS
