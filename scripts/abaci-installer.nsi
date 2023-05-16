; NSIS Installer script for the Quickstart Fortran Command Line

; ---------------- Properties ----------------
; Name used in installer GUI
Name "Abaci"

; Name for folder location and reg key
!define INSTALL_NAME "abaci"

; Name of Start Menu group folder
!define SM_FOLDER "BCI"

; Installer icon
!define MUI_ICON "../media/abaci.ico"

; Compress installer
SetCompress auto

; Always produce unicode installer
Unicode true

; ---------------- Setup ----------------
; Use EnVar plugin (https://nsis.sourceforge.io/EnVar_plug-in)
!addplugindir ".\nsis-plugins\EnVar_plugin\Plugins\x86-unicode"

Function FinishedInstall
ExecShell "open" "https://bristolcompositesinstitute.github.io/abaci/post-install.html"
FunctionEnd


; Use the 'Modern' Installer UI macros
!include "MUI2.nsh"

; Default installation folder (local)
InstallDir "$LOCALAPPDATA\${SM_FOLDER}\${INSTALL_NAME}"
  
; Get installation folder from registry if available
InstallDirRegKey HKCU "Software\${INSTALL_NAME}" ""

; Request application privileges
RequestExecutionLevel user


; ---------------- Installer Pages ----------------
!insertmacro MUI_PAGE_DIRECTORY
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE FinishedInstall
!insertmacro MUI_PAGE_INSTFILES


; ---------------- Uninstaller Pages ----------------
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

  
; MUI Language
!insertmacro MUI_LANGUAGE "English"


; ---------------- Component: Core Installation ----------------
Section "-Abaci" SecCore

  SetOutPath "$INSTDIR"

  File "..\src\abaci_main.py"
  File /r "..\src\abaci"
  File /r "..\src\redist"
  File /r "..\src\fortran"

  CreateDirectory "$INSTDIR\scripts"
  SetOutPath "$INSTDIR\scripts"
  File /r "..\scripts\abaci.cmd"

  ; Store installation folder
  WriteRegStr HKCU "Software\${INSTALL_NAME}" "" $INSTDIR
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add scripts folder to PATH for launcher
  EnVar::SetHKCU
  EnVar::AddValue "PATH" "$INSTDIR\scripts"

SectionEnd


; ---------------- Uninstaller ----------------
Section "Uninstall"

  RMDir /r "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\${INSTALL_NAME}"

  EnVar::SetHKCU

  EnVar::DeleteValue "PATH" "$INSTDIR\scripts"

SectionEnd


; ---------------- Component description Strings (EN) ----------------
LangString DESC_SecCore ${LANG_ENGLISH} "Abaci"
