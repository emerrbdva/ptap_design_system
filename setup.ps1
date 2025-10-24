# Pasos para iniciar el Sistema PTAP
# Este archivo te guía a través de la instalación y primer uso del sistema

# ============================================================================
# PASO 1: VERIFICAR PYTHON
# ============================================================================

Write-Host "=== VERIFICANDO PYTHON ===" -ForegroundColor Cyan
python --version

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Descarga Python 3.9+ desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Python detectado correctamente`n" -ForegroundColor Green

# ============================================================================
# PASO 2: CREAR ENTORNO VIRTUAL
# ============================================================================

Write-Host "=== CREANDO ENTORNO VIRTUAL ===" -ForegroundColor Cyan

if (Test-Path "venv") {
    Write-Host "Entorno virtual ya existe. Eliminando..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

python -m venv venv
Write-Host "✓ Entorno virtual creado`n" -ForegroundColor Green

# ============================================================================
# PASO 3: ACTIVAR ENTORNO VIRTUAL
# ============================================================================

Write-Host "=== ACTIVANDO ENTORNO VIRTUAL ===" -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo activar el entorno virtual" -ForegroundColor Red
    Write-Host "Si ves un error de política de ejecución, ejecuta:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Entorno virtual activado`n" -ForegroundColor Green

# ============================================================================
# PASO 4: ACTUALIZAR PIP
# ============================================================================

Write-Host "=== ACTUALIZANDO PIP ===" -ForegroundColor Cyan
python -m pip install --upgrade pip
Write-Host "✓ pip actualizado`n" -ForegroundColor Green

# ============================================================================
# PASO 5: INSTALAR DEPENDENCIAS
# ============================================================================

Write-Host "=== INSTALANDO DEPENDENCIAS ===" -ForegroundColor Cyan
Write-Host "Esto puede tomar varios minutos...`n" -ForegroundColor Yellow

pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Algunas dependencias no se pudieron instalar" -ForegroundColor Red
    Write-Host "Revisa los errores arriba y asegúrate de tener conexión a internet" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Dependencias instaladas correctamente`n" -ForegroundColor Green

# ============================================================================
# PASO 6: CREAR DIRECTORIOS NECESARIOS
# ============================================================================

Write-Host "=== CREANDO DIRECTORIOS ===" -ForegroundColor Cyan

$directories = @("data/cache", "data/snapshots", "data/exports", "data/projects", "logs")

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Creado: $dir" -ForegroundColor Green
    }
}

Write-Host "`n✓ Estructura de directorios lista`n" -ForegroundColor Green

# ============================================================================
# PASO 7: VERIFICAR OLLAMA (OPCIONAL - PARA IA)
# ============================================================================

Write-Host "=== VERIFICANDO OLLAMA (OPCIONAL) ===" -ForegroundColor Cyan
Write-Host "Ollama es necesario para las funciones de IA local`n" -ForegroundColor Yellow

$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue

if ($ollamaInstalled) {
    Write-Host "✓ Ollama detectado" -ForegroundColor Green
    
    Write-Host "`nDescargando modelos de IA (esto puede tomar mucho tiempo)..." -ForegroundColor Yellow
    Write-Host "Si ya tienes los modelos, puedes cancelar con Ctrl+C`n" -ForegroundColor Yellow
    
    # Preguntar al usuario
    $response = Read-Host "¿Deseas descargar los modelos ahora? (s/n)"
    
    if ($response -eq "s" -or $response -eq "S") {
        Write-Host "`nDescargando DeepSeek-R1:8b..." -ForegroundColor Cyan
        ollama pull deepseek-r1:8b
        
        Write-Host "`nDescargando Qwen2.5-Math:7b..." -ForegroundColor Cyan
        ollama pull qwen2.5-math:7b
        
        Write-Host "`nDescargando Mistral:7b-instruct-v0.3..." -ForegroundColor Cyan
        ollama pull mistral:7b-instruct-v0.3
        
        Write-Host "`n✓ Modelos de IA descargados" -ForegroundColor Green
    } else {
        Write-Host "Modelos omitidos. Puedes descargarlos más tarde con:" -ForegroundColor Yellow
        Write-Host "  ollama pull deepseek-r1:8b" -ForegroundColor Gray
        Write-Host "  ollama pull qwen2.5-math:7b" -ForegroundColor Gray
        Write-Host "  ollama pull mistral:7b-instruct-v0.3" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠ Ollama NO detectado" -ForegroundColor Yellow
    Write-Host "Para usar las funciones de IA, instala Ollama desde:" -ForegroundColor Yellow
    Write-Host "https://ollama.com/download" -ForegroundColor Cyan
    Write-Host "El sistema funcionará sin IA, pero sin redacción automática`n" -ForegroundColor Yellow
}

# ============================================================================
# PASO 8: EJECUTAR PRUEBA SIMPLE
# ============================================================================

Write-Host "`n=== EJECUTANDO PRUEBA SIMPLE ===" -ForegroundColor Cyan

Write-Host "Probando importaciones..." -ForegroundColor Yellow

python -c "import numpy; import scipy; import sympy; import pint; print('✓ Librerías científicas OK')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Problema con librerías científicas" -ForegroundColor Red
    exit 1
}

python -c "from reportlab.pdfgen import canvas; print('✓ ReportLab OK')"
python -c "import ezdxf; print('✓ ezdxf OK')"

Write-Host "`n✓ Todas las importaciones exitosas`n" -ForegroundColor Green

# ============================================================================
# FINALIZACIÓN
# ============================================================================

Write-Host "=" * 70 -ForegroundColor Green
Write-Host "INSTALACIÓN COMPLETADA EXITOSAMENTE" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green

Write-Host "`nPara ejecutar el sistema:" -ForegroundColor Cyan
Write-Host "  python app/main.py`n" -ForegroundColor White

Write-Host "Para ver ejemplos:" -ForegroundColor Cyan
Write-Host "  python examples/ejemplo_basico.py`n" -ForegroundColor White

Write-Host "Documentación:" -ForegroundColor Cyan
Write-Host "  Ver README.md y archivos en docs/`n" -ForegroundColor White

Write-Host "¡Sistema listo para usar!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
