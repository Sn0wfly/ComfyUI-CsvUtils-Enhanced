import os
import json
import base64
import hashlib
import zipfile
import tempfile
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    import folder_paths
except ImportError:
    class FolderPaths:
        output_directory = "C:\\ComfyUI\\output"
    folder_paths = FolderPaths()

# Google Drive imports (conditional)
try:
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    GOOGLE_AVAILABLE = True
    print("[CSV Cloud Sync] ✅ Google Drive dependencies loaded successfully")
except ImportError as e:
    GOOGLE_AVAILABLE = False
    print(f"[CSV Cloud Sync] ❌ Failed to load Google Drive dependencies: {e}")

class CSVCloudSync:
    """
    CSV Cloud Sync - Upload/Download automático para PC ↔ vast.ai
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["Upload", "Download"], {"default": "Upload"}),
                "google_credentials": ("STRING", {"default": "", "multiline": True, "placeholder": "Paste Google Service Account JSON here"}),
                "execute": ("BOOLEAN", {"default": False, "label_on": "Execute", "label_off": "Execute"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "cloud_sync"
    CATEGORY = "CSV Utils"
    OUTPUT_NODE = True
    
    def cloud_sync(self, mode, google_credentials, execute):
        """
        Cloud sync automático: Upload/Download preview + CSV
        """
        print(f"[CSV Cloud Sync] Mode: {mode}, Execute: {execute}")
        print(f"[CSV Cloud Sync] GOOGLE_AVAILABLE = {GOOGLE_AVAILABLE}")
        
        if not execute:
            result = "⏳ Ready to sync. Click Execute to start."
            print(f"[CSV Cloud Sync] {result}")
            return (result,)
        
        if not GOOGLE_AVAILABLE:
            result = "❌ ERROR: Install dependencies first:\npip install -r requirements-cloud.txt"
            print(f"[CSV Cloud Sync] {result}")
            print(f"[CSV Cloud Sync] GOOGLE_AVAILABLE is currently: {GOOGLE_AVAILABLE}")
            # Re-test dependencies
            try:
                from google.auth.transport.requests import Request
                print("[CSV Cloud Sync] Re-test: Google auth available")
            except ImportError as e:
                print(f"[CSV Cloud Sync] Re-test: Google auth failed: {e}")
            return (result,)
        
        if not google_credentials.strip():
            result = "❌ ERROR: Google credentials required.\nSee SETUP-15MIN.md for quick setup."
            print(f"[CSV Cloud Sync] {result}")
            return (result,)
        
        try:
            # Detectar archivos automáticamente
            output_dir = folder_paths.output_directory
            csv_path = os.path.join(output_dir, "prompt_history.csv")
            preview_dir = os.path.join(output_dir, "preview")
            
            print(f"[CSV Cloud Sync] Checking files:")
            print(f"[CSV Cloud Sync] - CSV: {csv_path} (exists: {os.path.exists(csv_path)})")
            print(f"[CSV Cloud Sync] - Preview: {preview_dir} (exists: {os.path.exists(preview_dir)})")
            
            # Validar setup
            validation_error = self._validate_setup(csv_path, preview_dir, mode)
            if validation_error:
                print(f"[CSV Cloud Sync] Validation failed: {validation_error}")
                return (validation_error,)
            
            # Configurar Google Drive
            try:
                service = self._setup_google_drive(google_credentials)
            except Exception as e:
                return (f"❌ GOOGLE DRIVE ERROR:\n{str(e)}\n\nCheck your JSON credentials.",)
            
            # Generar clave automática
            encryption_key = self._generate_auto_key(google_credentials)
            
            # Ejecutar modo
            if mode == "Upload":
                return self._upload_data(service, csv_path, preview_dir, encryption_key)
            else:
                return self._download_data(service, csv_path, preview_dir, encryption_key)
                
        except Exception as e:
            return (f"❌ UNEXPECTED ERROR:\n{str(e)}",)
    
    def _validate_setup(self, csv_path, preview_dir, mode):
        """Validar que tenemos los archivos necesarios"""
        if mode == "Upload":
            if not os.path.exists(csv_path):
                error = "❌ UPLOAD ERROR:\nNo CSV found at: output/prompt_history.csv\n\nUse CSV History Scanner first."
                print(f"[CSV Cloud Sync] {error}")
                return error
            
            if not os.path.exists(preview_dir):
                error = "❌ UPLOAD ERROR:\nNo preview folder found.\n\nUse CSV History Scanner to organize images first."
                print(f"[CSV Cloud Sync] {error}")
                return error
            
            # Contar archivos
            preview_files = [f for f in os.listdir(preview_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            print(f"[CSV Cloud Sync] Found {len(preview_files)} images in preview folder")
            
            if not preview_files:
                error = "❌ UPLOAD ERROR:\nPreview folder is empty.\n\nAdd some images with CSV History Scanner."
                print(f"[CSV Cloud Sync] {error}")
                return error
        
        print(f"[CSV Cloud Sync] Validation passed for {mode} mode")
        return None
    
    def _setup_google_drive(self, credentials_json):
        """Configurar Google Drive API"""
        try:
            credentials_data = json.loads(credentials_json)
        except json.JSONDecodeError:
            raise Exception("Invalid JSON format. Copy complete service account JSON.")
        
        credentials = service_account.Credentials.from_service_account_info(
            credentials_data,
            scopes=[
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        
        service = build('drive', 'v3', credentials=credentials)
        return service
    
    def _generate_auto_key(self, credentials_json):
        """Generar clave de encriptación automática desde credentials"""
        # Usar hash del JSON para generar clave consistente
        salt = hashlib.sha256(credentials_json.encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"csv-utils-encryption"))
        return Fernet(key)
    
    def _upload_data(self, service, csv_path, preview_dir, fernet):
        """Upload preview + CSV encriptado a Google Drive"""
        try:
            print("[CSV Cloud Sync] Starting upload...")
            
            # Crear ZIP temporal con todo
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                zip_path = temp_zip.name
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Agregar CSV
                zipf.write(csv_path, 'prompt_history.csv')
                
                # Agregar todas las imágenes de preview
                image_count = 0
                for root, dirs, files in os.walk(preview_dir):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            file_path = os.path.join(root, file)
                            arc_path = os.path.join('preview', file)
                            zipf.write(file_path, arc_path)
                            image_count += 1
            
            # Encriptar ZIP
            with open(zip_path, 'rb') as f:
                zip_data = f.read()
            
            encrypted_data = fernet.encrypt(zip_data)
            
            # Crear archivo encriptado temporal
            with tempfile.NamedTemporaryFile(suffix='.enc', delete=False) as temp_enc:
                temp_enc.write(encrypted_data)
                encrypted_path = temp_enc.name
            
            # Upload a Google Drive
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"csv_utils_backup_{timestamp}.enc"
            
            # Buscar o crear carpeta CSV Utils
            folder_id = self._get_or_create_folder(service, "CSV Utils Backups")
            
            # Upload archivo
            media = MediaFileUpload(encrypted_path, mimetype='application/octet-stream')
            request = service.files().create(
                body={
                    'name': file_name,
                    'parents': [folder_id]
                },
                media_body=media
            )
            response = request.execute()
            
            # Limpiar archivos temporales
            os.unlink(zip_path)
            os.unlink(encrypted_path)
            
            print(f"[CSV Cloud Sync] Upload completed: {file_name}")
            
            return (f"✅ UPLOAD SUCCESSFUL!\n\n📤 UPLOADED:\n- CSV: prompt_history.csv\n- Images: {image_count} files\n- Size: {len(encrypted_data)/1024:.1f} KB (encrypted)\n- File: {file_name}\n\n🔐 SECURITY:\n- Data encrypted before upload\n- Google only sees encrypted data\n- Auto-generated encryption key\n\n🎯 NEXT STEP:\nUse Download mode on vast.ai with same Google credentials.",)
            
        except Exception as e:
            return (f"❌ UPLOAD FAILED:\n{str(e)}",)
    
    def _download_data(self, service, csv_path, preview_dir, fernet):
        """Download y desencriptar desde Google Drive"""
        try:
            print("[CSV Cloud Sync] Starting download...")
            
            # Buscar carpeta CSV Utils
            folder_id = self._get_or_create_folder(service, "CSV Utils Backups")
            
            # Buscar el archivo más reciente
            results = service.files().list(
                q=f"'{folder_id}' in parents and name contains 'csv_utils_backup_' and name contains '.enc'",
                orderBy='createdTime desc',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return ("❌ DOWNLOAD ERROR:\nNo backup files found in Google Drive.\n\nUpload from your PC first.",)
            
            latest_file = files[0]
            file_name = latest_file['name']
            file_id = latest_file['id']
            
            # Download archivo encriptado
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                request = service.files().get_media(fileId=file_id)
                downloader = MediaIoBaseDownload(temp_file, request)
                
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                encrypted_path = temp_file.name
            
            # Desencriptar
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
            except Exception as e:
                os.unlink(encrypted_path)
                return ("❌ DECRYPTION ERROR:\nCannot decrypt data. Using different Google credentials?\n\nUse same credentials as upload device.",)
            
            # Extraer ZIP
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                temp_zip.write(decrypted_data)
                zip_path = temp_zip.name
            
            # Crear directorios si no existen
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            os.makedirs(preview_dir, exist_ok=True)
            
            # Clear preview directory for clean sync
            if os.path.exists(preview_dir):
                for f in os.listdir(preview_dir):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                        os.remove(os.path.join(preview_dir, f))
                print(f"[CSV Cloud Sync] Cleared local preview directory for clean sync")
            
            # Extraer contenido
            image_count = 0
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for member in zipf.namelist():
                    if member == 'prompt_history.csv':
                        zipf.extract(member, os.path.dirname(csv_path))
                        extracted_csv = os.path.join(os.path.dirname(csv_path), member)
                        if extracted_csv != csv_path:
                            import shutil
                            shutil.move(extracted_csv, csv_path)
                    elif member.startswith('preview/'):
                        # Extraer a preview directory
                        zipf.extract(member, os.path.dirname(preview_dir))
                        image_count += 1
            
            # Limpiar archivos temporales
            os.unlink(encrypted_path)
            os.unlink(zip_path)
            
            print(f"[CSV Cloud Sync] Download completed: {file_name}")
            
            return (f"✅ DOWNLOAD SUCCESSFUL!\n\n📥 DOWNLOADED:\n- CSV: prompt_history.csv\n- Images: {image_count} files\n- From: {file_name}\n- Decrypted: {len(decrypted_data)/1024:.1f} KB\n\n🔐 SECURITY:\n- Data decrypted successfully\n- Same encryption key verified\n- Ready to use locally\n\n🎯 READY:\n- Use CSV Prompt Search to browse\n- All images available in preview/\n- Your prompt collection is ready!",)
            
        except Exception as e:
            return (f"❌ DOWNLOAD FAILED:\n{str(e)}",)
    
    def _get_or_create_folder(self, service, folder_name):
        """Obtener o crear carpeta en Google Drive"""
        # Buscar carpeta existente
        results = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            pageSize=1
        ).execute()
        
        folders = results.get('files', [])
        if folders:
            print(f"[CSV Cloud Sync] Found existing folder: {folder_name}")
            return folders[0]['id']
        
        # Crear nueva carpeta
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata).execute()
        folder_id = folder['id']
        
        print(f"[CSV Cloud Sync] Created new folder: {folder_name} (ID: {folder_id})")
        
        # ACTIVADO: Compartir con tu cuenta personal
        # CAMBIA el email por el tuyo:
        YOUR_PERSONAL_EMAIL = "esnifer.rs@gmail.com"  # ← CAMBIA ESTO
        
        try:
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': YOUR_PERSONAL_EMAIL
            }
            service.permissions().create(
                fileId=folder_id,
                body=permission
            ).execute()
            print(f"[CSV Cloud Sync] Folder shared with {YOUR_PERSONAL_EMAIL}")
        except Exception as e:
            print(f"[CSV Cloud Sync] Could not share folder: {e}")
            print(f"[CSV Cloud Sync] Files still uploaded, just not visible in your personal Drive")
        
        return folder_id 