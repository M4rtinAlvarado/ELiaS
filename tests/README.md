# Tests - Módulo de Pruebas ELiaS

Este módulo contiene todas las pruebas, verificaciones y scripts de testing para el sistema ELiaS.

## 📁 Estructura

```
tests/
├── __init__.py                 # Inicialización del módulo
├── README.md                   # Esta documentación
├── run_all_tests.py           # Ejecutor principal de todos los tests
├── test_conexion.py           # Test básico de conexión
├── test_notion_fix.py         # Tests del sistema Notion
├── test_telegram_bot.py       # Tests completos del bot de Telegram
└── verificar_bot_completo.py  # Verificación final del bot complejo
```

## 🚀 Uso Rápido

### Ejecutar Todos los Tests
```bash
# Desde la raíz del proyecto
python tests/run_all_tests.py

# O usando módulos de Python
python -m tests.run_all_tests
```

### Ejecutar Tests Específicos
```bash
# Test de conexión básica
python tests/run_all_tests.py conexion

# Tests del sistema Notion
python tests/run_all_tests.py notion

# Tests del bot de Telegram
python tests/run_all_tests.py telegram

# Verificación completa
python tests/run_all_tests.py verificar
```

### Ejecutar Tests Individuales
```bash
# Test específico individual
python tests/test_conexion.py
python tests/test_notion_fix.py
python tests/test_telegram_bot.py
python tests/verificar_bot_completo.py
```

## 📋 Descripción de Tests

### `test_conexion.py`
- **Propósito**: Test básico de conectividad
- **Verifica**: 
  - Configuración del bot
  - Instalación de python-telegram-bot
  - Conexión básica con Telegram API

### `test_notion_fix.py`
- **Propósito**: Tests del sistema Notion
- **Verifica**:
  - Creación de objetos Tarea
  - Conexión a Notion API
  - Funcionamiento de servicios Notion
  - Creación de tareas completas

### `test_telegram_bot.py`
- **Propósito**: Suite completa de tests del bot
- **Verifica**:
  - Configuración completa
  - Dependencias instaladas
  - Módulos de ELiaS
  - Servicios inicializados
  - Creación del bot
  - Handlers configurados

### `verificar_bot_completo.py`
- **Propósito**: Verificación final antes de ejecutar
- **Verifica**:
  - Bot completo funcional
  - Todos los componentes listos
  - Configuración correcta

## 🎯 Interpretación de Resultados

### ✅ Test Exitoso
- Todos los componentes funcionan correctamente
- El sistema está listo para usar

### ❌ Test Fallido
- Hay problemas de configuración o dependencias
- Revisa los mensajes de error específicos

### ⚠️ Advertencias
- Funcionalidad parcial disponible
- Algunos servicios opcionales no disponibles

## 🔧 Solución de Problemas Comunes

### Error: "No se ha podido resolver la importación telegram"
```bash
pip install python-telegram-bot>=21.0.0
```

### Error: "TELEGRAM_BOT_TOKEN no configurado"
1. Crear bot con @BotFather en Telegram
2. Copiar token al archivo `.env`
3. `TELEGRAM_BOT_TOKEN=tu_token_aqui`

### Error: "NOTION_TOKEN no configurado"
1. Crear integración en Notion
2. Copiar token al archivo `.env`
3. `NOTION_TOKEN=tu_token_aqui`

### Error: "GOOGLE_API_KEY no configurado"
1. Crear API key en Google AI Studio
2. Copiar key al archivo `.env`
3. `GOOGLE_API_KEY=tu_key_aqui`

## 📊 Tests de Rendimiento

Los tests también verifican:
- Tiempo de inicialización de servicios
- Número de tareas y proyectos disponibles
- Estado de conexiones

## 🔄 Integración Continua

Estos tests pueden usarse en pipelines de CI/CD:

```yaml
# Ejemplo GitHub Actions
- name: Run ELiaS Tests
  run: |
    python tests/run_all_tests.py
```

## 📝 Agregar Nuevos Tests

1. Crear archivo `test_nuevo.py` en esta carpeta
2. Seguir el patrón de imports:
   ```python
   import sys
   from pathlib import Path
   ROOT_DIR = Path(__file__).parent.parent
   sys.path.insert(0, str(ROOT_DIR))
   ```
3. Implementar función `main()` o `run_all_tests()`
4. Agregar al diccionario en `run_all_tests.py`

## 🤖 Automatización

Los tests se pueden ejecutar automáticamente:
- Antes de cada deployment
- Después de cambios en configuración
- Como health check del sistema
- En tareas programadas

---

**¿Problemas con los tests?** Revisa los logs detallados que cada test proporciona para diagnosticar problemas específicos.