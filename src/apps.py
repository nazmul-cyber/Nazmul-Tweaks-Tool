"""Essential apps — winget install definitions."""

from dataclasses import dataclass


@dataclass
class App:
    id: str
    name: str
    description: str
    winget_id: str
    category: str
    icon: str = "📦"
    recommended: bool = False


ESSENTIAL_APPS: list[App] = [
    App("chrome", "Google Chrome", "Fast, popular web browser.", "Google.Chrome", "Browsers", "🌐", True),
    App("firefox", "Mozilla Firefox", "Privacy-focused browser.", "Mozilla.Firefox", "Browsers", "🦊"),
    App("brave", "Brave Browser", "Built-in ad blocker.", "Brave.Brave", "Browsers", "🦁"),
    App("7zip", "7-Zip", "Essential file archiver.", "7zip.7zip", "Utilities", "📦", True),
    App("vlc", "VLC Media Player", "Plays any media format.", "VideoLAN.VLC", "Utilities", "🎬", True),
    App("notepadpp", "Notepad++", "Lightweight text/code editor.", "Notepad++.Notepad++", "Utilities", "📝", True),
    App("everything", "Everything Search", "Instant file search.", "voidtools.Everything", "Utilities", "🔍"),
    App("sharex", "ShareX", "Screenshots & sharing.", "ShareX.ShareX", "Utilities", "📸"),
    App("dotnet8", ".NET 8 Runtime", "Required by many apps.", "Microsoft.DotNet.DesktopRuntime.8", "Microsoft", "🔷", True),
    App("vcredist", "VC++ Redistributable", "Required by games & apps.", "Microsoft.VCRedist.2015+.x64", "Microsoft", "🔷", True),
    App("powershell7", "PowerShell 7", "Modern PowerShell.", "Microsoft.PowerShell", "Microsoft", "💻", True),
    App("terminal", "Windows Terminal", "Modern terminal app.", "Microsoft.WindowsTerminal", "Microsoft", "💻", True),
    App("wingetui", "UniGetUI", "GUI package manager.", "MartiCliment.UniGetUI", "Microsoft", "📦"),
    App("git", "Git", "Version control.", "Git.Git", "Development", "🔧", True),
    App("vscode", "VS Code", "Code editor.", "Microsoft.VisualStudioCode", "Development", "💻"),
    App("python", "Python 3.12", "Python language.", "Python.Python.3.12", "Development", "🐍"),
    App("nodejs", "Node.js LTS", "JavaScript runtime.", "OpenJS.NodeJS.LTS", "Development", "🟢"),
    App("discord", "Discord", "Voice & text chat.", "Discord.Discord", "Communication", "💬"),
    App("zoom", "Zoom", "Video calls.", "Zoom.Zoom", "Communication", "📹"),
    App("teams", "Microsoft Teams", "Microsoft collaboration.", "Microsoft.Teams", "Communication", "💼"),
    App("acrobat", "Adobe Acrobat Reader", "PDF reader.", "Adobe.Acrobat.Reader.64-bit", "Documents", "📄", True),
    App("libreoffice", "LibreOffice", "Free office suite.", "TheDocumentFoundation.LibreOffice", "Documents", "📊"),
    App("bitwarden", "Bitwarden", "Password manager.", "Bitwarden.Bitwarden", "Security", "🔐", True),
]

APP_CATEGORIES = ["Browsers", "Utilities", "Microsoft", "Development", "Communication", "Documents", "Security"]
FRESH_APP_IDS = [a.id for a in ESSENTIAL_APPS if a.recommended]