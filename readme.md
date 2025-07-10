# ComfyUI CSV Utils - Enhanced

> **A complete solution for managing your ComfyUI prompts and images** ��  
> Save, organize, sync and navigate your prompt collection with cloud backup

## 📋 What is this?

**ComfyUI CSV Utils Enhanced** is a **5-node system** that converts scattered prompt chaos into an organized, searchable, and cloud-synced collection. Think of it as your **personal prompt library** with integrated image viewer and **cross-device sync**.

### 🎯 Problem it solves:
- ❌ Lost prompts after generating images
- ❌ Good images mixed with failed experiments  
- ❌ Hard to find which prompt generated which image
- ❌ No way to review your previous work
- ❌ **Can't access prompts on different machines (PC ↔ vast.ai)**

### ✅ What you get:
- 🏛️ **Organized library** of prompts and images
- 🔍 **Visual search** with thumbnails and zoom
- 🤖 **Automatic extraction** of prompts from images
- 📁 **Automatic organization** of files
- 💾 **Persistent memory** - remembers your preferences
- ☁️ **Cloud sync** - access your collection anywhere (PC ↔ vast.ai)
- 🔐 **Privacy-first** - encrypted cloud storage

---

## 🚀 Quick Installation

### Basic Installation (Local Use)
1. **Clone or download** this repository to your ComfyUI `custom_nodes` folder:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/yourrepository/ComfyUI-CsvUtils.git
   ```

2. **Restart ComfyUI** completely

3. **Done!** You'll find the nodes in the **"CSV Utils"** category

### Cloud Sync Installation (PC ↔ vast.ai)
1. **Install cloud dependencies**:
   ```bash
   cd ComfyUI/custom_nodes/ComfyUI-CsvUtils
   pip install -r requirements-cloud.txt
   ```

2. **Follow the 15-minute setup guide**: See [SETUP-15MIN.md](SETUP-15MIN.md)

3. **Restart ComfyUI** - you'll now have the **CSV Cloud Sync** node available

---

## 🎓 Beginner Tutorial

### Step 1: Generate Images (As usual)
- Use ComfyUI normally to generate images
- Images are saved in `ComfyUI/output/` with automatic metadata

### Step 2: Review your History 
1. **Add the "CSV History Scanner" node** to your workflow
2. **Adjust `max_images`** (how many images to review, e.g., 50)
3. **Click "Scan"** - a panel will open with your recent images
4. **Review the groups** - images with identical prompts appear grouped

### Step 3: Select the Best Ones
- **Click on thumbnails** to see images full-size (with zoom and pan)
- **Use checkboxes** to select:
  - ✅ **Complete groups** (title checkbox)
  - ✅ **Individual images** (each image's checkbox)
- **"Select All" / "Select None"** for quick selection

### Step 4: Organize your Collection
- **Click "Move & Save Selected"**
- **Automagic!** The system:
  - 📁 Moves selected images to `output/preview/`
  - 📊 Saves prompts to `output/prompt_history.csv`
  - 🚫 Prevents duplicates automatically

### Step 5: Navigate your Library
1. **Add "CSV Prompt Search"** to any workflow
2. **Path auto-completes** with `output/prompt_history.csv`
3. **Navigate your collection** with thumbnails and zoom
4. **Use saved prompts** as reference or starting point

### Step 6: Cloud Sync (Optional)
1. **Add "CSV Cloud Sync"** node for cross-device access
2. **Upload** your collection from PC
3. **Download** on vast.ai or other machines
4. **Work seamlessly** across devices

---

## 🛠️ The 5 Nodes Explained

### 🔧 1. CSV Prompt Saver
> **For when you want to save prompts manually**

**When to use**: You have a specific prompt you want to save without reviewing the complete history.

**Inputs**:
- `positive_prompt`: Your positive prompt
- `negative_prompt`: Your negative prompt (optional)
- `file_path`: Where to save (e.g., `prompts.csv`)
- `image_path`: Associated image(s) (optional)

**Tip**: You can connect the output of your text nodes directly here.

### 🔍 2. CSV Prompt Search
> **Your visual prompt browser**

**When to use**: You want to explore your collection, find a specific prompt, or use one as base for new creations.

**Key features**:
- 🧠 **Automatic memory** - remembers the last CSV path used
- 🖼️ **Visual grid** with thumbnails of all your images
- 🔍 **Modal with zoom** - scroll to zoom, drag to pan
- ⌨️ **Keyboard controls** - arrows, Escape, etc.
- 📁 **Smart search** - finds images in subdirectories automatically

**Viewer controls**:
- `Mouse scroll`: Zoom in/out (10% - 500%)
- `Click and drag`: Move zoomed image
- `Escape or click outside`: Close
- `Arrows ←/→`: Navigate between multiple images

### 📸 3. CSV History Scanner ⭐
> **The system's heart - reviews and organizes automatically**

**When to use**: After an image generation session, to review what went well and organize your collection.

**What it does**:
1. **Scans** your `output/` folder looking for recent PNGs
2. **Extracts prompts** automatically from ComfyUI metadata
3. **Groups** images with identical prompts
4. **Shows** everything in a visual interface
5. **Organizes** whatever you select into your personal library

**Configuration**:
- `max_images`: How many images to review (10-200, recommended: 50-100)
- `scan_button`: Click to execute

**Results panel**:
- **Groups by prompt** - all images with the same prompt appear together
- **Individual thumbnails** - preview of each image
- **Flexible selection** - by complete group or individual image
- **Modal view** - click any thumbnail to see full-size

### 📥 4. CSV Prompt Loader
> **Load saved prompts into your workflow**

**When to use**: You want to use a previously saved prompt as starting point for new generations.

**Key features**:
- 🎯 **Direct integration** with your CSV files
- 🔄 **Quick loading** of positive and negative prompts
- 🔍 **Easy browsing** through your prompt history

### ☁️ 5. CSV Cloud Sync ⭐ NEW!
> **Sync your collection across devices**

**When to use**: You want to access your prompt collection on different machines (PC, vast.ai, etc.).

**Key features**:
- 🔐 **Privacy-first** - automatic encryption (Google never sees your prompts)
- 🚀 **15-minute setup** - follow [SETUP-15MIN.md](SETUP-15MIN.md)
- 📤 **Upload mode** - backup your collection to Google Drive
- 📥 **Download mode** - restore collection on new machine (replaces local files)
- 🔄 **Automatic** - detects CSV and preview folder automatically
- 🚫 **Smart collision prevention** - unique timestamp renaming prevents image conflicts

**Perfect for**:
- **PC → vast.ai workflow** (no image name collisions)
- **Multiple workstations**
- **Backup and restore**
- **Team collaboration**

---

## 🎯 Recommended Workflows

### 🔄 Daily Workflow (Local)
```
1. Generate images with ComfyUI (normal)
2. CSV History Scanner → Scan
3. Select the best images/groups
4. "Move & Save Selected" 
5. CSV Prompt Search to navigate your collection
```

### ☁️ Cloud Workflow (PC ↔ vast.ai)
```
PC:
1. Generate and organize with History Scanner
2. CSV Cloud Sync → Upload

vast.ai:
1. CSV Cloud Sync → Download
2. Work with your prompts normally
3. CSV Cloud Sync → Upload (new work)

PC:
4. CSV Cloud Sync → Download (sync back)
```

### 🎨 Creative Workflow
```
1. CSV Prompt Search → find inspiration in your library
2. CSV Prompt Loader → load base prompt
3. Modify and generate new variations
4. CSV History Scanner → organize the new results
```

### 📚 Archive Workflow
```
1. CSV Prompt Saver → save special prompts manually
2. CSV Prompt Search → review and organize existing collection
3. Use web interface to clean duplicates
```

---

## 📁 File Organization

### Automatic Structure
```
ComfyUI/output/
├── temp_image1.png       # ⏳ Recently generated images
├── temp_image2.png       # ⏳ (temporary, unorganized)
├── preview/              # 📚 Your organized library
│   ├── landscape1.png   # ✅ Curated images
│   ├── portrait2.png    # ✅ (moved automatically)
│   └── ...
└── prompt_history.csv    # 📊 Prompt database
```

### Simple CSV Format
```csv
positive_prompt,negative_prompt,image_path
"beautiful portrait, detailed, 4k",bad quality,"preview/portrait1.png;preview/portrait2.png"
"mountain landscape, sunset",blurry,"preview/landscape.png"
```

**Format features**:
- **Multiple images**: Separated by `;` or `,`
- **UTF-8 encoding**: Full support for accents and special characters
- **Relative paths**: Automatically relative to output folder
- **No duplicates**: System prevents repeated entries automatically

---

## 🎮 Controls Guide

### Image Modal (Zoom Viewer)
| Action | Control |
|--------|---------|
| Zoom In/Out | Mouse wheel |
| Move image | Click and drag |
| Close modal | `Escape`, click outside, or ❌ button |
| Next image | Right arrow `→` |
| Previous image | Left arrow `←` |
| Reset zoom | Double click |

### History Scanner Panel
| Element | Function |
|----------|---------|
| Title checkbox | Select complete group |
| Image checkbox | Select individual image |
| "Select All" | Select everything visible |
| "Select None" | Deselect everything |
| "Move & Save" | Organize selected items |
| Panel header | Drag to move panel |
| Panel edges | Drag to resize |

---

## 🧠 Smart Functions

### 💾 Persistent Memory
- **CSV Prompt Search remembers** automatically the last path used
- **Persists between sessions** - works after ComfyUI restarts
- **Informative toast** tells you when loading saved path
- **Smart default value** - suggests `output/prompt_history.csv` if first time

### 🔍 Advanced Image Search
The system searches for images automatically in priority order:
1. **Exact path** specified in CSV
2. **Preview folder** - `preview/image.png`
3. **Root folder** - `image.png`
4. **Recursive search** in all subdirectories

### 🚫 Duplicate Prevention
- **Automatic detection** of identical prompts
- **Smart grouping** of multiple images with same prompt
- **Informative alerts** when duplicates are prevented

### 🖼️ Metadata Processing
- **Automatic extraction** from ComfyUI PNG metadata
- **Smart detection** of positive vs negative prompts
- **Robust handling** of different workflow formats

### 🚫 Smart Collision Prevention
- **Unique timestamp renaming** - prevents image name conflicts between sessions
- **Cross-device safety** - work on PC and vast.ai without overwriting images
- **Format**: `ComfyUI_00001_1703901234567.png` (original name + millisecond timestamp)
- **Automatic handling** - no manual intervention required

---

## 🔧 Troubleshooting

### ❓ "Images don't show"
**Possible causes**:
- Incorrect paths in CSV
- Images moved or deleted
- Permission issues

**Solutions**:
1. ✅ Verify that CSV paths are correct
2. ✅ Use relative paths to `output/` folder
3. ✅ System will search automatically in subdirectories
4. ✅ Check that images haven't been moved manually

### ❓ "History Scanner doesn't find images"
**Possible causes**:
- Images without ComfyUI metadata
- Non-PNG files
- Corrupted metadata

**Solutions**:
1. ✅ Only processes PNGs with embedded ComfyUI workflow
2. ✅ Increase `max_images` if there are many images in output
3. ✅ Verify images were generated with ComfyUI (not external)

### ❓ "Prompts not extracted"
**Possible causes**:
- Images generated with very old versions
- Workflow without text nodes
- Damaged metadata

**Solutions**:
1. ✅ Make sure images contain `CLIPTextEncode` nodes
2. ✅ External images won't have ComfyUI metadata
3. ✅ Regenerate problematic images with current ComfyUI

### ❓ "Panel closes by itself"
**Solutions**:
1. ✅ Make sure you have enough screen space
2. ✅ Drag panel from header (not from edges)
3. ✅ Use ❌ button to close intentionally

---

## 🎨 Advanced Use Cases

### 📊 Prompt Analysis
- Use CSV Prompt Search to review which prompts generate better results
- Identify patterns in your most successful prompts
- Experiment with variations of saved prompts

### 🎭 Character Management
- Organize prompts by specific characters or styles
- Create "thematic libraries" using different CSV files
- Use multiple images per entry for character variations

### 🏗️ Production Workflows
- Separate experiments (temporary output) from final work (organized preview)
- Maintain a central CSV for the entire project
- Use memory functionality for repetitive workflows

### 🎓 Learning and Improvement
- Document your evolution comparing old vs new prompts
- Identify which keywords generate better results
- Create reference library for future projects

---

## 📈 Versions and Changelog

### 🆕 v3.1 (Current) - Smart Sync & Collision Prevention
- 🚫 **Smart collision prevention** - unique timestamp renaming prevents image conflicts
- 🔧 **Simplified cloud sync** - cleaner download process without backup clutter
- ✅ **Session safety** - work on multiple devices without image overwrites
- 🎯 **Perfect PC ↔ vast.ai workflow** - seamless cross-device development

### 📚 v3.0 - Cloud Sync Release
- ☁️ **CSV Cloud Sync** - Cross-device synchronization (PC ↔ vast.ai)
- 🔐 **Privacy-first encryption** - Google never sees your prompts
- 📥 **CSV Prompt Loader** - Easy integration of saved prompts
- 🚀 **15-minute setup** for cloud functionality
- 📦 **Optional dependencies** - cloud features don't affect core functionality
- 🎯 **5-node complete system** for professional workflows

### 📚 v2.1
- ✨ **CSV History Scanner** - Automatic prompt extraction
- 🎨 **Enhanced zoom modal** with pan and keyboard controls
- 📁 **Full subdirectory support** and smart search
- 🖼️ **Multiple images per entry** with automatic navigation
- 💾 **Persistent memory** for CSV Prompt Search
- 🏗️ **Automatic file organization**
- 🚫 **Enhanced duplicate prevention**
- 🎯 **Modern interface** and responsive

### 📚 v2.0
- Complete system refactoring
- Renewed web interface
- Performance improvements

### 🌱 v1.0
- Basic CSV Prompt Saver and Search
- Core CSV functionality

---

## 🤝 Contributing

Have ideas for improvements? Found a bug? 

1. **Open an Issue** describing the problem or suggestion
2. **Fork the repository** if you want to contribute code
3. **Pull Request** with your improvements

**Areas where contributions would help**:
- 🌍 Translations to other languages
- 🎨 UI/UX improvements
- 🐛 Report and fix bugs
- 📚 Documentation and examples
- 🔧 New features

---

## 📄 License

This project is under MIT license. See `LICENSE.md` file for complete details.

---

## 🙏 Acknowledgments

Developed for the ComfyUI community with love ❤️

**Like this project?** 
- ⭐ Give it a star on GitHub
- 🔄 Share it with other ComfyUI users
- 💬 Leave feedback in Issues

---

> **💡 Final tip**: This README might seem long, but the daily workflow is super simple:  
> `Generate → Scan → Select → Move & Save → Navigate`  
> Everything else is automatic! 🚀