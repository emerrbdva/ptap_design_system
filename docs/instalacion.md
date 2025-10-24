# Guía de Instalación

## Requisitos del Sistema

### Hardware Mínimo
- **CPU**: Procesador de 4 núcleos (recomendado 8+ para modelos IA grandes)
- **RAM**: 8 GB mínimo (16 GB recomendado)
- **Disco**: 20 GB libres (para modelos de IA)
- **OS**: Windows 10/11, Linux, macOS

### Software Necesario
- **Python**: 3.9 o superior
- **pip**: Incluido con Python
- **Ollama**: (Opcional) Para funciones de IA local

---

## Instalación Paso a Paso

### Windows

#### 1. Instalar Python

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, marca "Add Python to PATH"
3. Verifica la instalación:
   ```powershell
   python --version
   ```

#### 2. Clonar o Descargar el Proyecto

Si usas Git:
```powershell
git clone <url-del-repositorio>
cd ptap_design_system
```

Si descargaste un ZIP:
- Extrae el contenido
- Abre PowerShell en el directorio

#### 3. Ejecutar Script de Instalación Automática

```powershell
.\setup.ps1
```

Este script:
- ✅ Crea entorno virtual
- ✅ Instala dependencias
- ✅ Crea estructura de directorios
- ✅ Verifica instalación
- ✅ (Opcional) Descarga modelos de IA

**Nota**: Si hay error de política de ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Instalar Ollama (Opcional - para IA)

1. Descarga desde [ollama.com](https://ollama.com/download)
2. Instala el ejecutable
3. Abre una terminal y ejecuta:
   ```powershell
   ollama serve
   ```
4. En otra terminal, descarga los modelos:
   ```powershell
   ollama pull deepseek-r1:8b
   ollama pull qwen2.5-math:7b
   ollama pull mistral:7b-instruct-v0.3
   ```

**Tamaños de modelos**:
- `deepseek-r1:8b` - ~4.5 GB
- `qwen2.5-math:7b` - ~4 GB
- `mistral:7b-instruct-v0.3` - ~4 GB

---

### Linux / macOS

#### 1. Instalar Python

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

**macOS** (con Homebrew):
```bash
brew install python@3.9
```

#### 2. Clonar el Proyecto

```bash
git clone <url-del-repositorio>
cd ptap_design_system
```

#### 3. Instalación Manual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate  # Linux/macOS

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios
mkdir -p data/{cache,snapshots,exports,projects} logs
```

#### 4. Instalar Ollama (Opcional)

**Linux**:
```bash
curl https://ollama.ai/install.sh | sh
ollama serve &
ollama pull deepseek-r1:8b
ollama pull qwen2.5-math:7b
ollama pull mistral:7b-instruct-v0.3
```

**macOS**:
- Descarga desde [ollama.com](https://ollama.com/download)
- Instala la aplicación
- Ejecuta los comandos `ollama pull`

---

## Instalación Manual de Dependencias

Si prefieres instalar paso a paso:

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Científicas
pip install numpy scipy sympy pint

# IA
pip install ollama langchain langchain-community

# Web
pip install flask fastapi uvicorn

# Reportes
pip install reportlab openpyxl xlsxwriter python-docx

# CAD
pip install ezdxf

# Conectores
pip install requests sodapy aiohttp paho-mqtt

# Utilidades
pip install pyyaml python-dotenv loguru matplotlib seaborn plotly

# Desarrollo
pip install pytest pytest-cov black flake8
```

---

## Verificación de Instalación

### Verificar Python y Dependencias

```bash
python -c "import numpy, scipy, sympy, pint; print('✓ Científicas OK')"
python -c "from reportlab.pdfgen import canvas; print('✓ ReportLab OK')"
python -c "import ezdxf; print('✓ ezdxf OK')"
```

### Verificar Ollama

```bash
ollama list
```

Deberías ver los modelos descargados.

### Ejecutar Ejemplo

```bash
python examples/ejemplo_basico.py
```

Si todo funciona, verás el diseño de una PTAP de 50 L/s.

---

## Solución de Problemas

### Error: "No module named 'pint'"

```bash
pip install pint
```

### Error: "Cannot connect to Ollama"

1. Verifica que Ollama esté ejecutándose:
   ```bash
   ollama serve
   ```

2. Verifica el host en `config/config.yaml`:
   ```yaml
   ai_models:
     ollama:
       host: "http://localhost:11434"
   ```

### Error: Política de ejecución (Windows)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problemas con ReportLab en Windows

Instala Visual C++ Build Tools:
- Descarga desde [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

---

## Siguiente Paso

Una vez instalado, consulta:
- [Manual de Usuario](manual_usuario.md)
- [Ejemplos de Uso](../examples/)
- [README.md](../README.md)

---

## Soporte

Si tienes problemas:
1. Revisa esta guía completa
2. Verifica los logs en `logs/`
3. Abre un issue en GitHub con detalles del error
