import platform


def detectar_so():
    """Devuelve 'Windows', 'Darwin' (macOS) o 'Linux'."""
    return platform.system()


def detectar_distro_linux():
    """Lee /etc/os-release para identificar la distro (ubuntu, debian, fedora, arch, etc.)."""
    try:
        with open("/etc/os-release") as f:
            datos = {}
            for linea in f:
                if "=" in linea:
                    clave, valor = linea.strip().split("=", 1)
                    datos[clave] = valor.strip('"')
        return datos.get("ID", "").lower()
    except FileNotFoundError:
        return ""


def instalar_ffmpeg_windows():
    print("🔧 Instalando ffmpeg con winget...")
    try:
        subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg"], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  winget falló o no está disponible. Probando con Chocolatey...")
        try:
            subprocess.run(["choco", "install", "ffmpeg", "-y"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            sys.exit(
                "❌ No se pudo instalar automáticamente.\n"
                "   Instala winget (App Installer, viene con Windows 10/11) o Chocolatey."
            )


def instalar_ffmpeg_macos():
    print("🔧 Instalando ffmpeg con Homebrew...")
    try:
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.exit("❌ Homebrew no encontrado. Instálalo desde https://brew.sh primero.")


def instalar_ffmpeg_linux():
    distro = detectar_distro_linux()
    print(f"🔧 Distribución detectada: {distro or 'desconocida'}")

    gestores = {
        "ubuntu": (
            ["sudo", "apt-get", "update"],
            ["sudo", "apt-get", "install", "-y", "ffmpeg"],
        ),
        "debian": (
            ["sudo", "apt-get", "update"],
            ["sudo", "apt-get", "install", "-y", "ffmpeg"],
        ),
        "fedora": (None, ["sudo", "dnf", "install", "-y", "ffmpeg"]),
        "centos": (None, ["sudo", "dnf", "install", "-y", "ffmpeg"]),
        "arch": (None, ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"]),
        "manjaro": (None, ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"]),
        "opensuse": (None, ["sudo", "zypper", "install", "-y", "ffmpeg"]),
    }

    entrada = gestores.get(distro)
    if not entrada:
        sys.exit(
            f"❌ Distro '{distro}' no reconocida automáticamente.\n"
            "   Instala ffmpeg manualmente con el gestor de paquetes de tu sistema."
        )

    update_cmd, install_cmd = entrada
    if update_cmd:
        subprocess.run(update_cmd, check=True)
    subprocess.run(install_cmd, check=True)


def asegurar_ffmpeg():
    """Verifica ffmpeg; si no está, intenta instalarlo automáticamente según el SO."""
    if shutil.which("ffmpeg") is not None:
        return

    print("⚠️  ffmpeg no encontrado. Intentando instalación automática...")
    sistema = detectar_so()

    if sistema == "Windows":
        instalar_ffmpeg_windows()
    elif sistema == "Darwin":
        instalar_ffmpeg_macos()
    elif sistema == "Linux":
        instalar_ffmpeg_linux()
    else:
        sys.exit(f"❌ Sistema operativo no soportado: {sistema}")

    if shutil.which("ffmpeg") is None:
        sys.exit("❌ La instalación automática no funcionó. Instálalo manualmente.")

    print("✅ ffmpeg instalado correctamente.")
