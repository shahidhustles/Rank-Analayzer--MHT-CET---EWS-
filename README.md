# EWS Rank Analyzer

A Flask web application that analyzes merit rank PDFs to determine EWS (Economically Weaker Section) category rank based on general merit rank.

## 🎯 Purpose

This application solves the problem of finding your EWS category rank when you only know your general merit rank. It scans through the merit list PDF and counts how many EWS candidates are ranked above you to determine your actual EWS rank.

## 🚀 Features

- **PDF Analysis**: Processes large merit list PDFs (6000+ pages) efficiently
- **EWS Rank Calculation**: Counts EWS candidates up to your merit rank
- **Web Interface**: Clean, responsive web interface
- **Real-time Processing**: Shows loading state while analyzing PDF
- **Error Handling**: Comprehensive error handling and user feedback

## 📋 How It Works

1. **Input**: Student enters their general merit rank number
2. **Processing**: Application scans the PDF from rank 1 to the entered rank
3. **Counting**: Counts all candidates with "Yes" in the EWS column
4. **Result**: Returns the EWS rank (count of EWS candidates above your rank)

## 🛠️ Installation

1. **Clone or download** the project files
2. **Navigate** to the project directory:
   ```bash
   cd "Rank Analayzer"
   ```
3. **Create virtual environment** (if not already created):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```
4. **Install dependencies**:
   ```bash
   pip install flask PyPDF2 pandas tabula-py pdfplumber
   ```

## 🎮 Usage

1. **Start the application**:

   ```bash
   python app.py
   ```

2. **Open your browser** and go to: `http://127.0.0.1:5000`

3. **Enter your merit rank** in the form and click "Analyze EWS Rank"

4. **Wait for processing** (may take a moment for large PDFs)

5. **View your EWS rank** in the results

## 📁 File Structure

```
Rank Analayzer/
├── app.py                  # Main Flask application
├── merit-ranks.pdf         # Merit list PDF file
├── test_parser.py         # Test script for PDF parsing
├── templates/
│   └── index.html         # Web interface template
├── .venv/                 # Virtual environment
└── README.md              # This file
```

## 🔧 Technical Details

### PDF Processing

- Uses `pdfplumber` library for robust PDF text and table extraction
- Handles both table-based and text-based PDF formats
- Implements fallback parsing methods for different PDF structures

### Data Parsing

- Extracts merit rank from the first column
- Searches for "Yes" in EWS column (typically column 6-8)
- Validates data integrity and handles parsing errors gracefully

### Web Interface

- Responsive design with modern CSS
- AJAX-based form submission for better UX
- Loading states and comprehensive error handling
- Real-time feedback during PDF processing

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_parser.py
```

This will test:

- Individual line parsing from PDF
- PDF processing with sample merit numbers
- Error handling and edge cases

## ⚡ Performance

- **Large PDFs**: Efficiently handles 6000+ page PDFs
- **Memory Usage**: Processes pages sequentially to minimize memory usage
- **Speed**: Stops processing once target merit rank is reached

## 🎓 Example Usage

**Input**: Merit Rank 1250
**Process**: Scan ranks 1-1250, count EWS candidates
**Output**: "Your EWS rank is 85 (out of candidates up to merit rank 1250)"

## 🔍 Troubleshooting

### Common Issues:

1. **PDF not found**: Ensure `merit-ranks.pdf` is in the project directory
2. **Parsing errors**: Check PDF format matches expected structure
3. **Slow processing**: Large PDFs may take time; be patient
4. **Merit rank not found**: Ensure the rank exists in the PDF

### Debug Mode:

The application runs in debug mode by default, showing detailed error messages in the console.

## 📝 Notes

- **PDF Format**: Designed for Maharashtra State CET merit lists
- **EWS Column**: Looks for "Yes" values in the EWS column
- **Data Validation**: Includes checks for data integrity and format
- **Development**: Uses Flask development server (not for production)

## 🤝 Contributing

Feel free to improve the parsing logic, add new features, or enhance the user interface!

## 📄 License

This project is for educational purposes. Ensure compliance with relevant data usage policies.
