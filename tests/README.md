# 🧪 Tests - Módulo de Pruebas ELiaS

Este módulo contiene todas las pruebas, verificaciones, scripts de testing y **sistema de benchmark** para evaluar el sistema ELiaS.

## 📁 Estructura

```
tests/
├── __init__.py                 # Inicialización del módulo
├── README.md                   # Esta documentación
├── run_all_tests.py            # Ejecutor principal de todos los tests
├── benchmark_bot.py            # 🆕 Benchmark con banco de 39 preguntas
├── test_conexion.py            # Test básico de conexión
├── test_notion_fix.py          # Tests del sistema Notion
├── test_telegram_bot.py        # Tests completos del bot de Telegram
└── verificar_bot_completo.py   # Verificación final del bot
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

## 📊 Sistema de Benchmark (NUEVO)

El archivo `benchmark_bot.py` contiene un banco de **39 preguntas** organizadas en 5 categorías para evaluar el bot sistemáticamente.

### Ejecutar Benchmark Completo

```bash
python tests/benchmark_bot.py
```

### Ejecutar por Categoría

```bash
# Solo pruebas de creación de tareas (11 preguntas)
python tests/benchmark_bot.py --categoria crear_tarea

# Solo pruebas de creación de eventos (9 preguntas)
python tests/benchmark_bot.py --categoria crear_evento

# Solo pruebas de consultas (10 preguntas)
python tests/benchmark_bot.py --categoria consultar

# Solo pruebas ambiguas (6 preguntas)
python tests/benchmark_bot.py --categoria ambiguo

# Pruebas mixtas/complejas (3 preguntas)
python tests/benchmark_bot.py --categoria mixto
```

### Guardar Resultados

```bash
# Guardar en JSON
python tests/benchmark_bot.py --output resultados.json

# Guardar categoría específica
python tests/benchmark_bot.py --categoria crear_evento --output eventos.json
```

### Categorías del Benchmark

| Categoría | Preguntas | Descripción |
|-----------|-----------|-------------|
| `crear_tarea` | 11 | Creación de tareas con diferentes formatos |
| `crear_evento` | 9 | Creación de eventos con fechas y ubicaciones |
| `consultar` | 10 | Consultas sobre tareas, eventos, proyectos |
| `ambiguo` | 6 | Mensajes que requieren clarificación |
| `mixto` | 3 | Casos complejos y edge cases |

### Ejemplo de Salida del Benchmark

```
🔬 BENCHMARK DE ELIAS BOT
═══════════════════════════════════════════════════════

📂 Categoría: crear_tarea (11 preguntas)
───────────────────────────────────────────────────────
1/11 │ "Crear tarea: estudiar para el examen de cálculo"
     │ Esperado: CREAR_TAREA
     │ Resultado: ✅ CREAR_TAREA
     │ Tiempo: 0.45s
───────────────────────────────────────────────────────
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
  - Creación de objetos Tarea y Evento
  - Conexión a Notion API
  - Funcionamiento de servicios Notion
  - Creación de tareas y eventos completos

### `test_telegram_bot.py`
- **Propósito**: Suite completa de tests del bot
- **Verifica**:
  - Configuración completa
  - Dependencias instaladas
  - Módulos de ELiaS
  - Servicios inicializados
  - Creación del bot
  - Handlers configurados

### `benchmark_bot.py` (NUEVO)
- **Propósito**: Evaluación sistemática del bot
- **Verifica**:
  - Clasificación de intenciones (CREAR_TAREA, CREAR_EVENTO, CONSULTAR, AMBIGUO)
  - Extracción de datos de tareas (nombre, prioridad, fecha, tiempo_estimado)
  - Extracción de datos de eventos (nombre, fecha, ubicación, tipo)
  - Respuestas a consultas de información
  - Manejo de casos ambiguos

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

### Agregar Preguntas al Benchmark

Para agregar nuevas preguntas al benchmark, edita `benchmark_bot.py`:

```python
PREGUNTAS = {
    "crear_tarea": [
        {"texto": "Tu nueva pregunta aquí", "esperado": "CREAR_TAREA"},
        # ...
    ],
    "crear_evento": [
        {"texto": "Nuevo evento de prueba", "esperado": "CREAR_EVENTO"},
        # ...
    ]
}
```

## 🤖 Automatización

Los tests se pueden ejecutar automáticamente:
- Antes de cada deployment
- Después de cambios en configuración
- Como health check del sistema
- En tareas programadas
- **Benchmark antes de cambios en IA**

### Integración Continua

```yaml
# Ejemplo GitHub Actions
name: ELiaS Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: python tests/run_all_tests.py
      - name: Run Benchmark
        run: python tests/benchmark_bot.py --output benchmark_results.json
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark_results.json
```

---

**¿Problemas con los tests?** Revisa los logs detallados que cada test proporciona para diagnosticar problemas específicos.