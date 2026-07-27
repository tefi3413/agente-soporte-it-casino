import os
import shutil
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import ChatCohere
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PDF_PATH = "manual_soporte_it_casinos.pdf"
INDEX_PATH = "faiss_index"

app = Flask(__name__)
cadena = None
retriever = None

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agente IT - Casinos del Río</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: sans-serif; background: #0f0f1a; color: #e0e0e0; height: 100vh; display: flex; flex-direction: column; }
  header { background: #1a1a2e; padding: 16px 24px; border-bottom: 1px solid #333; }
  header h1 { font-size: 18px; color: #fff; }
  header p { font-size: 13px; color: #888; margin-top: 4px; }
  #chat { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
  .msg { max-width: 75%; padding: 12px 16px; border-radius: 12px; font-size: 14px; line-height: 1.6; }
  .user { background: #16213e; align-self: flex-end; color: #90caf9; }
  .bot { background: #1e1e2e; align-self: flex-start; color: #e0e0e0; border: 1px solid #333; }
  .bot .fuente { font-size: 11px; color: #666; margin-top: 8px; }
  .thinking { color: #888; font-style: italic; }
  footer { padding: 16px 24px; background: #1a1a2e; border-top: 1px solid #333; display: flex; gap: 10px; }
  footer input { flex: 1; padding: 10px 16px; border-radius: 8px; border: 1px solid #444; background: #0f0f1a; color: #fff; font-size: 14px; outline: none; }
  footer input:focus { border-color: #4a90d9; }
  footer button { padding: 10px 20px; background: #4a90d9; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
  footer button:hover { background: #357abd; }
  footer button:disabled { background: #333; cursor: not-allowed; }
</style>
</head>
<body>
<header>
  <h1>🎰 Agente de Soporte IT — Casinos del Río</h1>
  <p>Consultá el manual de procedimientos en lenguaje natural</p>
</header>
<div id="chat">
  <div class="msg bot">¡Hola! Soy el asistente de soporte IT de Casinos del Río. Podés preguntarme sobre procedimientos, contactos, sistemas o políticas de seguridad.</div>
</div>
<footer>
  <input type="text" id="input" placeholder="Escribí tu pregunta..." onkeydown="if(event.key==='Enter') enviar()"/>
  <button id="btn" onclick="enviar()">Enviar</button>
</footer>
<script>
async function enviar() {
  const input = document.getElementById('input');
  const btn = document.getElementById('btn');
  const chat = document.getElementById('chat');
  const pregunta = input.value.trim();
  if (!pregunta) return;

  input.value = '';
  btn.disabled = true;

  chat.innerHTML += `<div class="msg user">${pregunta}</div>`;
  chat.innerHTML += `<div class="msg bot thinking" id="thinking">🔍 Buscando en el manual...</div>`;
  chat.scrollTop = chat.scrollHeight;

  try {
    const res = await fetch('/preguntar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({pregunta})
    });
    const data = await res.json();
    document.getElementById('thinking').remove();
    chat.innerHTML += `<div class="msg bot">${data.respuesta}<div class="fuente">📖 Fuente: páginas ${data.paginas} del manual</div></div>`;
  } catch(e) {
    document.getElementById('thinking').remove();
    chat.innerHTML += `<div class="msg bot">❌ Error al consultar el agente.</div>`;
  }

  btn.disabled = false;
  chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>
"""

def inicializar():
    global cadena, retriever
    print("🧠 Cargando modelo de embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    if not os.path.exists(INDEX_PATH):
        print("📄 Procesando PDF...")
        loader = PyPDFLoader(PDF_PATH)
        paginas = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        fragmentos = splitter.split_documents(paginas)
        vectorstore = FAISS.from_documents(fragmentos, embeddings)
        vectorstore.save_local(INDEX_PATH)
    else:
        print("⚡ Cargando índice existente...")
        vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

    llm = ChatCohere(model="command-r-plus-08-2024", temperature=0.1, cohere_api_key=COHERE_API_KEY)
    prompt = PromptTemplate.from_template("""Sos el asistente de soporte IT de Casinos del Río.
Respondé en español, de forma clara y concisa, basándote ÚNICAMENTE en el contexto provisto.
Si la información no está en el contexto, decí que no encontraste esa información en el manual.

Contexto:
{context}

Pregunta: {question}

Respuesta:""")

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    cadena = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("✅ Agente listo.")

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/preguntar", methods=["POST"])
def preguntar():
    data = request.get_json()
    pregunta = data.get("pregunta", "")
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    respuesta = cadena.invoke(pregunta)
    docs = retriever.invoke(pregunta)
    paginas = sorted(set(doc.metadata.get("page", 0) + 1 for doc in docs if isinstance(doc.metadata.get("page"), int)))
    return jsonify({"respuesta": respuesta, "paginas": paginas})

if __name__ == "__main__":
    inicializar()
    app.run(host="0.0.0.0", port=5000, debug=False)
