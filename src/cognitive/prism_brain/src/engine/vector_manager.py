import os

# ChromaDB 텔레메트리 및 허깅페이스 서버 접속 완전 봉쇄 (최우선 순위)
os.environ["CHROMA_TELEMETRY_DISABLED"] = "True"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import shutil

class VectorManager:
    def __init__(self, db_path="data/chroma_db"):
        self.db_path = db_path
        try:
            # local_files_only=True 옵션을 사용하여 오프라인 모드 강제 적용
            self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2",
                local_files_only=True
            )
        except Exception as e:
            error_str = str(e).lower()
            if "net" in error_str or "connection" in error_str or "dns" in error_str or "host" in error_str or "closed" in error_str or "offline" in error_str:
                raise Exception(
                    "Failed to initialize embedding model in offline mode. "
                    "Ensure model is cached via 'scripts/download_model.py'."
                ) from e
            else:
                raise e

        # Settings 객체를 통해 텔레메트리 및 내부 스레드 설정 최적화 >> 서버 기동 순서랑 그런거 바꾸면서 
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True,
                allow_reset=True
            )
        )

    def update_collection(self, collection_name: str, documents: list, metadatas: list, ids: list):
        try:
            self.client.delete_collection(collection_name)
        except:
            pass 
        
        collection = self.client.create_collection(
            name=collection_name, 
            embedding_function=self.ef
        )
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        print(f"[VectorManager] {collection_name} 업데이트 완료. ({len(documents)}건)")

    def search(self, collection_name: str, query_text: str, n_results=5):
        try:
            collection = self.client.get_collection(
                name=collection_name, 
                embedding_function=self.ef
            )
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"[VectorManager] 검색 중 오류 ({collection_name}): {e}")
            return None
