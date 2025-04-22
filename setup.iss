[Setup]
AppName=Invoice Reader
AppVersion=1.0
DefaultDirName={pf}\Invoice Reader
DefaultGroupName=Invoice Reader
OutputDir=dist
OutputBaseFilename=InvoiceReader_Setup
SetupIconFile="C:\Users\emmes\Documents\Python Scripts\InvoiceReader\assets\invoice.ico"
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Invoice Reader.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Invoice Reader"; Filename: "{app}\Invoice Reader.exe"; IconFilename: "{app}\Invoice Reader.exe"
Name: "{userdesktop}\Invoice Reader"; Filename: "{app}\Invoice Reader.exe"; IconFilename: "{app}\Invoice Reader.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crea un'icona sul desktop"; GroupDescription: "Icone:"
