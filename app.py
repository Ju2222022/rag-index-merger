import streamlit as st
import faiss
import json
import tempfile
import os

st.set_page_config(page_title="Fusion Index RAG", layout="centered")
st.title("🔗 Fusionneur de fichiers d'index RAG (.faiss + .json)")

uploaded_faiss = st.file_uploader("📁 Upload les fichiers `.faiss`", type="faiss", accept_multiple_files=True)
uploaded_jsons = st.file_uploader("📁 Upload les fichiers `.json`", type="json", accept_multiple_files=True)

if st.button("Fusionner"):
    if len(uploaded_faiss) != len(uploaded_jsons):
        st.error("Tu dois uploader autant de fichiers `.faiss` que de fichiers `.json`")
    elif not uploaded_faiss:
        st.error("Aucun fichier fourni")
    else:
        st.info("Fusion en cours...")

        # Créer un dossier temporaire
        with tempfile.TemporaryDirectory() as tempdir:
            all_chunks = []
            faiss_indexes = []

            # Sauvegarder et charger chaque couple
            for faiss_file, json_file in zip(uploaded_faiss, uploaded_jsons):
                faiss_path = os.path.join(tempdir, faiss_file.name)
                json_path = os.path.join(tempdir, json_file.name)

                with open(faiss_path, "wb") as f:
                    f.write(faiss_file.read())

                with open(json_path, "wb") as f:
                    f.write(json_file.read())

                # Charger l'index
                index = faiss.read_index(faiss_path)
                faiss_indexes.append(index)

                # Charger les chunks
                with open(json_path, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                    all_chunks.extend(chunks)

            # Fusionner FAISS
            final_index = faiss_indexes[0]
            for idx in faiss_indexes[1:]:
                final_index.merge_from(idx)

            # Export final
            final_index_path = os.path.join(tempdir, "final_index.faiss")
            final_chunks_path = os.path.join(tempdir, "final_chunks.json")

            faiss.write_index(final_index, final_index_path)
            with open(final_chunks_path, "w", encoding="utf-8") as f:
                json.dump(all_chunks, f, ensure_ascii=False, indent=2)

            # Téléchargement
            st.success("Fusion terminée ✅")

            with open(final_index_path, "rb") as f:
                st.download_button("📥 Télécharger `final_index.faiss`", f, file_name="final_index.faiss")

            with open(final_chunks_path, "rb") as f:
                st.download_button("📥 Télécharger `final_chunks.json`", f, file_name="final_chunks.json")
