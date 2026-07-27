# 🎰 Agente de IA - Soporte IT Casinos del Río

Agente de inteligencia artificial que responde preguntas sobre el Manual de Soporte IT de Casinos del Río. Desarrollado como parte del Challenge de Alura Latam.

---

## 🧠 Descripción del proyecto

Muchas empresas pierden horas buscando información dentro de documentos internos. Este proyecto resuelve ese problema: un agente de IA que cualquier persona del equipo de IT puede consultar en lenguaje natural, sin necesidad de abrir el manual.

El agente lee el PDF del manual, indexa su contenido y responde preguntas directas como:
- *"¿Cómo reinicio una maquina tragamonedas offline?"*
- *"¿Qué hago si hay un incidente de seguridad?"*
- *"¿A quién escalo si cae el servidor de base de datos?"*

---

## 🏗️ Arquitectura

```
Usuario → Pregunta en texto
              ↓
        Agente LangChain
              ↓
    FAISS (búsqueda vectorial)
    Encuentra los 4 fragmentos más relevantes del PDF
              ↓
        Google Gemini
    Genera respuesta en lenguaje natural
              ↓
        Respuesta al usuario
              ↑
    (con número de página fuente)
```

**Flujo de preparación del documento (una sola vez):**
```
PDF → PyPDF (extrae texto) → RecursiveTextSplitter (divide en fragmentos)
    → Embeddings de Google → FAISS (guarda el índice en disco)
```

---

## 🛠️ Tecnologías utilizadas

| Componente | Herramienta | Descripción |
|---|---|---|
| Lenguaje | Python 3.10+ | Lenguaje principal |
| Framework de agente | LangChain | Orquestación del agente y cadena QA |
| Modelo de lenguaje | Google Gemini 1.5 Flash | Generación de respuestas |
| Embeddings | Google Embedding-001 | Conversión de texto a vectores |
| Base vectorial | FAISS | Búsqueda de similitud semántica |
| Lectura de PDF | PyPDF | Extracción de texto del manual |
| Variables de entorno | python-dotenv | Gestión segura de API keys |

---

## ⚙️ Instrucciones para ejecutar el proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/agente-soporte-it-casinos.git
cd agente-soporte-it-casinos
```

### 2. Crear un entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la API key de Google AI
```bash
cp .env.example .env
```
Abrí el archivo `.env` y reemplazá `tu_api_key_aqui` con tu API key.

> Podés obtener una API key gratuita en: https://aistudio.google.com/app/apikey

### 5. Colocar el PDF en la carpeta del proyecto
Asegurate de que el archivo `manual_soporte_it_casinos.pdf` esté en la misma carpeta que `agente.py`.

### 6. Ejecutar el agente
```bash
python agente.py
```

---

## 💬 Ejemplos de preguntas y respuestas

**Pregunta:** ¿Cuál es el procedimiento para resetear la contraseña de un usuario?

**Respuesta:**
> Para resetear la contraseña de un usuario, seguí estos pasos:
> 1. Verificá la identidad del solicitante presencialmente o via su supervisor.
> 2. Accedé a Usuarios y Equipos de Active Directory en SRV-DC01.
> 3. Buscá el usuario por nombre o legajo.
> 4. Click derecho > Restablecer contraseña.
> 5. Ingresá la contraseña temporal: Casino2025!
> 6. Marcá "El usuario debe cambiar la contraseña en el próximo inicio de sesión".
> 7. Registrá el incidente en el sistema de tickets.
> 
> 📖 Fuente: páginas [3] del manual

---

**Pregunta:** ¿A qué número llamo si hay un problema con el sistema IGT?

**Respuesta:**
> El soporte técnico de IGT está disponible las 24 horas los 7 días de la semana. El número es 0800-448-4357. También podés contactarlos por email a soporte@igt.com
> 
> 📖 Fuente: páginas [4, 5] del manual

---

**Pregunta:** ¿Cuándo debo escalar un incidente a Nivel 3?

**Respuesta:**
> Debés escalar a Nivel 3 (Emergencia) cuando se presente alguna de estas situaciones:
> - Caída total de la red del casino
> - Servidor de base de datos SRV-SQL01 inaccesible
> - Sistema IGT completamente caído
> - Incidente de seguridad confirmado (ransomware, brecha de datos)
> - Falla total en el sistema de cámaras
> - Cualquier incidente que requiera cierre parcial o total de operaciones
> El tiempo de respuesta para Nivel 3 es inmediato.
> 
> 📖 Fuente: páginas [4] del manual

---

## ☁️ Deploy en OCI

La aplicación fue desplegada en Oracle Cloud Infrastructure (OCI Compute).

- **URL pública:** http://167.126.25.38:5000
<img width="2561" height="951" alt="agentee" src="https://github.com/user-attachments/assets/f23e8340-7ee2-4150-a147-72fa1a5c8346" />


---

## 📁 Estructura del proyecto

```
agente-soporte-it-casinos/
├── agente.py                         # Código principal del agente
├── manual_soporte_it_casinos.pdf     # Documento fuente
├── requirements.txt                  # Dependencias del proyecto
├── .env.example                      # Template de variables de entorno
├── .env                              # Variables de entorno (NO subir a GitHub)
├── faiss_index/                      # Índice vectorial (generado automáticamente)
└── README.md                         # Este archivo
```

---

## 👤 Autor

Desarrollado por Estefania Alejandra Uribe para el Challenge Agente de Alura Latam.
