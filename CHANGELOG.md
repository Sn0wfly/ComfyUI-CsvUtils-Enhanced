# Changelog

All notable changes to ComfyUI CSV Utils Enhanced will be documented in this file.

## [3.0.0] - 2024-07-10 - Cloud Sync Release

### 🆕 Major New Features
- **CSV Cloud Sync Node** - Cross-device synchronization between PC and vast.ai
- **Privacy-First Encryption** - Automatic encryption using Google Drive credentials
- **15-Minute Setup** - Complete cloud sync setup in just 15 minutes
- **CSV Prompt Loader Node** - Load saved prompts directly into workflows

### ☁️ Cloud Sync Features
- **Upload Mode** - Backup your entire collection (CSV + images) to Google Drive
- **Download Mode** - Restore collection on any machine with same credentials
- **Automatic Detection** - Finds CSV and preview folder automatically
- **Encrypted Storage** - Google never sees your actual prompts
- **Smart Compression** - Efficient ZIP compression with metadata preservation

### 🔧 Technical Improvements
- **Optional Dependencies** - Cloud features don't affect core functionality
- **Graceful Fallback** - System works perfectly without cloud dependencies
- **Enhanced Error Handling** - Clear error messages and troubleshooting
- **Automatic Key Generation** - No manual encryption key management

### 📦 Installation
- **requirements-cloud.txt** - Optional dependencies for cloud features
- **Conditional Imports** - Core nodes work independently
- **Setup Guide** - Comprehensive SETUP-15MIN.md documentation

### 🎯 Use Cases
- **PC → vast.ai Workflow** - Seamless prompt collection transfer
- **Multiple Workstations** - Access your library anywhere
- **Backup & Restore** - Professional-grade backup solution
- **Team Collaboration** - Share encrypted collections safely

---

## [2.1.0] - 2024-06-01 - History Scanner Release

### 🆕 Major Features
- **CSV History Scanner** - Automatic prompt extraction from images
- **Visual Selection Interface** - Modern UI for reviewing and organizing
- **Automatic File Organization** - Smart movement of selected images

### 🎨 UI/UX Improvements
- **Enhanced Zoom Modal** - Pan, zoom, and keyboard navigation
- **Responsive Grid Layout** - Optimal viewing on all screen sizes
- **Persistent Memory** - Remembers last used CSV path
- **Progress Indicators** - Clear feedback during operations

### 🔍 Advanced Features
- **Smart Grouping** - Groups images with identical prompts
- **Bulk Selection** - Select entire groups or individual images
- **Duplicate Prevention** - Automatic detection and prevention
- **Metadata Processing** - Robust handling of ComfyUI workflows

---

## [2.0.0] - 2024-04-01 - Complete Refactor

### 🏗️ System Overhaul
- **Complete Code Refactoring** - Modern, maintainable architecture
- **New Web Interface** - Professional UI with modern design
- **Performance Improvements** - Faster image loading and processing
- **Enhanced Error Handling** - Better user feedback and debugging

### 🖼️ Image Handling
- **Multiple Images per Entry** - Support for image collections
- **Subdirectory Search** - Automatic image discovery
- **Thumbnail Generation** - Fast preview loading
- **Zoom and Pan** - Professional image viewer

---

## [1.0.0] - 2024-01-01 - Initial Release

### 🌱 Core Features
- **CSV Prompt Saver** - Manual prompt saving functionality
- **CSV Prompt Search** - Basic search and navigation
- **CSV File Management** - Core CSV operations
- **Basic Web Interface** - Simple UI for prompt management

### 📁 File Organization
- **CSV Format** - Simple, readable prompt storage
- **Image Associations** - Link prompts to generated images
- **Path Management** - Relative path handling
- **UTF-8 Support** - Full Unicode character support

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in backwards compatible manner  
- **PATCH** version for backwards compatible bug fixes

## Contributing

See [Contributing Guidelines](CONTRIBUTING.md) for information on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details. 