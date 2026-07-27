import os
import shutil
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
if not COHERE_API_KEY:
    raise ValueError("Falta la variable COHERE_API_KEY en el archivo .env")

PDF_PATH = "manual_soporte_it_casinos.pdf"
INDEX_PATH = "faiss_index"

def cargar_documento(pdf_path):
    print(f"📄 Cargando documento: {pdf_path}")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No se encontró '{pdf_path}'.")
    loader = PyPDFLoader(pdf_path)
    paginas = loader.load()
    print(f"   → {len(paginas)} páginas cargadas")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    fragmentos = splitter.split_documents(paginas)
    print(f"   → {len(fragmentos)} fragmentos generados")
    return fragmentos

def obtener_vectorstore(fragmentos, embeddings):
    if os.path.exists(INDEX_PATH):
        print("⚡ Cargando índice vectorial existente...")
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    print("🔨 Creando índice vectorial...")
    vectorstore = FAISS.from_documents(fragmentos, embeddings)
    vectorstore.save_local(INDEX_PATH)
    print(f"   → Índice guardado en '{INDEX_PATH}/'")
    return vectorstore

def crear_cadena_qa(vectorstore):
    llm = ChatCohere(model="command-r-plus-08-2024", temperature=0.1, cohere_api_key=COHERE_API_KEY)

    prompt = PromptTemplate.from_template("""Sos el asistente de soporte IT de Casinos del Río.
Respondé en español, de forma clara y concisa, basándote ÚNICAMENTE en el contexto provisto.
Si la información no está en el contexto, decí que no encontraste esa información en el manual.

Contexto del manual:
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
    return cadena, retriever

def chat(cadena, retriever):
    print("\n" + "=" * 60)
    print("🤖 Agente de Soporte IT - Casinos del Río")
    print("=" * 60)
    print("Escribí tu pregunta y presioná Enter. Escribí 'salir' para terminar.\n")
    while True:
        try:
            pregunta = input("Tu pregunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Hasta luego!")
            break
        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit"}:
            print("👋 ¡Hasta luego!")
            break
        print("\n🔍 Buscando en el manual...")
        respuesta = cadena.invoke(pregunta)
        print("\n📋 Respuesta:")
        print("-" * 50)
        print(respuesta)
        print("-" * 50)
        docs = retriever.invoke(pregunta)
        if docs:
            paginas = sorted(set(doc.metadata.get("page", 0) + 1 for doc in docs if isinstance(doc.metadata.get("page"), int)))
            print(f"📖 Fuente: páginas {paginas} del manual\n")
        else:
            print()

def main():
    print("🧠 Cargando modelo de embeddings local...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    if os.path.exists(INDEX_PATH):
        shutil.rmtree(INDEX_PATH)
        print("🗑️  Índice anterior eliminado, recreando...")
    fragmentos = cargar_documento(PDF_PATH)
    vectorstore = obtener_vectorstore(fragmentos, embeddings)
    cadena, retriever = crear_cadena_qa(vectorstore)
    print("\n✅ Agente listo.")
    chat(cadena, retriever)

if __name__ == "__main__":
    main()
