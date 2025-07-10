# ⏱️ CSV Cloud Sync - 15 Minute Setup

Get your prompt collection syncing between PC and vast.ai in just 15 minutes!

## 🎯 **What You'll Get**

```
PC → Upload → Google Drive (encrypted)
vast.ai → Download → Ready to work
```

**Privacy**: Google only sees encrypted data. Your prompts stay private.

---

## ⏰ **Step 1: Google Cloud Setup (5 minutes)**

### 🔧 **Create Project & API**

1. **Go to**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Create new project**:
   - Click "Select a project" → "New Project"
   - Name: `CSV Utils Sync`
   - Click "Create"

3. **Enable Google Drive API**:
   - Search "Google Drive API" in top bar
   - Click "Google Drive API" → "Enable"

### 🔑 **Create Service Account**

4. **Go to Credentials**:
   - Left menu → "Credentials"
   - Click "Create Credentials" → "Service account"

5. **Fill details**:
   - Service account name: `csv-sync`
   - Service account ID: `csv-sync` (auto-filled)
   - Click "Create and Continue"

6. **Skip role assignment**:
   - Click "Continue" (no roles needed)
   - Click "Done"

7. **Create key**:
   - Click on your new service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" → "Create"
   - **Save the downloaded JSON file!**

---

## ⏰ **Step 2: ComfyUI Setup (2 minutes)**

### 📦 **Install Dependencies**

```bash
cd ComfyUI/custom_nodes/ComfyUI-CsvUtils
pip install -r requirements-cloud.txt
```

### 🔄 **Restart ComfyUI**

Close and restart ComfyUI completely.

---

## ⏰ **Step 3: Configure Node (3 minutes)**

### 🔧 **Add Node**

1. **Right-click** in ComfyUI canvas
2. **Search**: "CSV Cloud Sync"
3. **Add** the node

### 📋 **Configure**

1. **Open your JSON file** (from Step 1)
2. **Copy ALL content** (Ctrl+A, Ctrl+C)
3. **Paste** into `google_credentials` field
4. **Set mode**: "Upload"
5. **Click Execute**: False → True

---

## ⏰ **Step 4: Test Upload (3 minutes)**

### 📤 **First Upload**

1. **Make sure you have**:
   - `output/prompt_history.csv` (use CSV History Scanner first)
   - `output/preview/` with some images

2. **Execute the node**
3. **Should see**: ✅ UPLOAD SUCCESSFUL!

### ✅ **Verify**

Check your Google Drive → "CSV Utils Backups" folder should appear with encrypted file.

---

## ⏰ **Step 5: Test Download (2 minutes)**

### 📥 **Test Download** (simulate vast.ai)

1. **Change mode**: "Download"
2. **Execute** the node
3. **Should see**: ✅ DOWNLOAD SUCCESSFUL!

### ✅ **Verify**

Your `output/` folder should have your CSV and preview images restored.

---

## 🎉 **You're Done! (Total: 15 minutes)**

### 🚀 **Daily Workflow**

**On PC**:
```
1. Generate images
2. CSV History Scanner → organize
3. CSV Cloud Sync → Upload
```

**On vast.ai**:
```
1. CSV Cloud Sync → Download
2. Work with your prompts normally
3. CSV Cloud Sync → Upload (if you add more)
```

### 🔐 **Security**

- ✅ **Auto-encryption**: Based on your Google credentials
- ✅ **Private**: Google never sees your actual prompts
- ✅ **Seamless**: Same credentials = automatic sync

---

## 🚨 **Troubleshooting**

### **"No CSV found"**
```
Use CSV History Scanner first to create prompt_history.csv
```

### **"Invalid JSON format"**
```
Copy the COMPLETE JSON file content, including { } brackets
```

### **"Google Drive error"**
```
- Check JSON is complete and valid
- Verify Google Drive API is enabled
- Make sure service account was created correctly
```

### **"No backup files found"**
```
Upload from PC first before downloading on vast.ai
```

---

## 🎯 **Pro Tips**

1. **Save your JSON file**: Keep it safe for future setups
2. **Same credentials everywhere**: Use exact same JSON on PC and vast.ai
3. **Upload first**: Always upload from PC before downloading elsewhere
4. **Organize first**: Use CSV History Scanner before uploading

---

## 📱 **vast.ai Quick Setup**

When you start a new vast.ai instance:

```bash
# 1. Install CSV Utils
cd ComfyUI/custom_nodes
git clone [your-repo-url]
cd ComfyUI-CsvUtils
pip install -r requirements-cloud.txt

# 2. Restart ComfyUI
# 3. Add CSV Cloud Sync node
# 4. Paste same JSON credentials
# 5. Set mode to "Download"
# 6. Execute → Your prompts are ready!
```

**Time on vast.ai**: ~3 minutes total setup

---

**🎉 Total setup time: 15 minutes once, 3 minutes on each new vast.ai instance!** 