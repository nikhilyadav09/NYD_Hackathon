# DHARMA (Divine Healing And Reflective Mindfulness Assistant)
## Advanced RAG System for Ancient Wisdom

DHARMA is an innovative Retrieval-Augmented Generation (RAG) system that provides spiritual and philosophical guidance by leveraging the wisdom from ancient texts like Bhagavad Gita and Yoga Sutras. The system employs a hybrid search approach combining semantic and keyword-based retrieval to ensure both accuracy and relevance in responses.

## 🌟 Features

- Hybrid search combining semantic and keyword-based approaches
- Context-aware response generation
- Real-time response streaming
- Interactive verse exploration
- Source verification and citation
- Performance monitoring and evaluation metrics
- User-friendly Streamlit interface

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ with pgvector extension
- Groq API access (for LLM)
- 8GB RAM minimum
- Git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nikhilyadav09/ancient-wisdom-rage.git
   cd ancient-wisdom-rage
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL with pgvector**
   ```bash
   # Install PostgreSQL and pgvector extension
   sudo apt-get install postgresql postgresql-contrib
   git clone https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   make install
   ```

5. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   DB_NAME=ancient_wisdoms
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   GROQ_API_KEY=your_groq_api_key
   ```



## 🚀 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Access the interface**
   Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

3. **Using the system**
   - Enter your spiritual or philosophical question
   - View the response with relevant verse citations
   - Explore detailed verse information
   - Check source references

## 📊 Evaluation

Run the evaluation pipeline to measure system performance:
```bash
python src/evaluation/run_evaluation.py
```

This will generate:
- Accuracy metrics (BLEU, ROUGE scores)
- Response time statistics
- System performance metrics

## 🗂️ Project Structure

```
NYD_HACKATHONE/
├── src/
│   ├── config/
│   │   ├── prompts.py      # Response templates
│   │   └── settings.py     # Configuration
│   ├── core/
│   │   ├── generator.py    # Response generation
│   │   ├── pipeline.py     # Main RAG pipeline
│   │   ├── query_preprocessor.py # Query processing
│   │   └── retriever.py    # Verse retrieval
│   └── evaluation/
|        ├──run_evaluation.py
│        └── evaluator.py    # Performance metrics
├── app.py                    # Streamlit interface
├── data/
│   └── files              # Source text data             
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🔍 API Response Format

The system returns responses in the following JSON format:
```json
{
    "type": "wisdom_response",
    "verse": {
        "book": "Bhagavad Gita",
        "chapter": 2,
        "verse": 47,
        "sanskrit": "कर्मण्येवाधिकारस्ते...",
        "translation": "You have a right to perform your prescribed duty...",
        "explanation": "This verse emphasizes the importance of..."
    },
    "response": {
        "summary": "The wisdom from Bhagavad Gita teaches us...",
        "sources": ["Bhagavad Gita 2.47", "Yoga Sutras 1.2"]
    }
}
```

## 📊 Performance Metrics

Current system performance:
- Average Response Time: 1.17s
- Semantic Similarity: 0.85
- BLEU Score: 0.72
- ROUGE-1: 0.76
- Cache Hit Rate: 85%

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- DHARMA team

## 🙏 Acknowledgments

- Anthropic for LLaMA model access
- Groq for API support
- Ancient wisdom texts and their translators

## 🆘 Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL service
   sudo service postgresql status
   
   # Restart if needed
   sudo service postgresql restart
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Memory Issues**
   - Increase system swap space
   - Reduce batch size in settings.py

## 📧 Contact

For any queries or support:
- Email: nikhilyadav1921@gmail.com
- GitHub Issues: [Create New Issue](https://github.com/nikhilyadav09/ancient-wisdom-rage/issues)