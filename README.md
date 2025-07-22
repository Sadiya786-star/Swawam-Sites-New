# 🤖 Streamlit Claude App

A modern, clean Streamlit web application that provides secure user authentication and AI-powered prompt generation using Claude 3 Sonnet via OpenRouter API.

## ✨ Features

- **🔐 Secure Authentication**: Simple login system with session management
- **📊 User Activity Logging**: Automatic logging of user activities to CSV
- **🤖 AI Integration**: Claude 3 Sonnet via OpenRouter API with key rotation
- **🎨 Modern UI**: Clean, minimalistic design using Streamlit components
- **🚀 Deployment Ready**: Optimized for Hugging Face Spaces deployment

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd streamlit-claude-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenRouter API keys:
   ```env
   OPENROUTER_API_KEY_1=your_first_api_key_here
   OPENROUTER_API_KEY_2=your_second_api_key_here
   OPENROUTER_API_KEY_3=your_third_api_key_here
   OPENROUTER_API_KEY_4=your_fourth_api_key_here
   ```

3. Get API keys from [OpenRouter](https://openrouter.ai/keys)

### 4. Run the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 👥 Demo Accounts

The application includes several demo accounts for testing:

| Username | Password |
|----------|----------|
| admin    | password123 |
| user     | user123 |
| demo     | demo123 |
| test     | test123 |

## 📁 Project Structure

```
streamlit-claude-app/
├── app.py                 # Main Streamlit application
├── auth.py               # Authentication utilities
├── api_client.py         # API integration functions
├── utils.py              # Helper functions
├── user_log.csv          # User login activity log (auto-created)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API keys)
├── .env.example         # Example environment file
└── README.md            # This file
```

## 🚀 Deployment to Hugging Face Spaces

### Method 1: Direct Upload

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces)
2. Choose "Streamlit" as the SDK
3. Upload all files except `.env`
4. Add your API keys as Space secrets:
   - Go to Settings → Repository secrets
   - Add each API key as a secret (OPENROUTER_API_KEY_1, etc.)

### Method 2: Git Repository

1. Push your code to a Git repository
2. Connect the repository to Hugging Face Spaces
3. Configure environment variables in Space settings

### Environment Variables for Deployment

Make sure to set these environment variables in your deployment platform:

- `OPENROUTER_API_KEY_1`
- `OPENROUTER_API_KEY_2`
- `OPENROUTER_API_KEY_3`
- `OPENROUTER_API_KEY_4`

## 🔧 Configuration

### Authentication

The app uses simple username/password authentication. To modify users, edit the `VALID_USERS` dictionary in `auth.py`:

```python
VALID_USERS = {
    "your_username": "your_password",
    # Add more users as needed
}
```

### API Configuration

The app automatically rotates between 4 API keys to avoid rate limits. You can modify the API settings in `api_client.py`.

## 📊 User Activity Logging

All user login activities are automatically logged to `user_log.csv` with the following information:

- Username
- Login timestamp
- Session ID

## 🛡️ Security Features

- Environment-based API key management
- Session state management
- Input validation
- Error handling for API failures
- No sensitive data in logs

## 🐛 Troubleshooting

### Common Issues

1. **API Keys Not Working**
   - Verify keys are correctly set in `.env`
   - Check OpenRouter account balance
   - Ensure keys have proper permissions

2. **CSV Logging Errors**
   - Check file permissions in deployment directory
   - Ensure write access to application directory

3. **Authentication Issues**
   - Verify username/password combinations
   - Check session state initialization

### Error Messages

The app provides detailed error messages for:
- Invalid API keys
- Network connection issues
- Authentication failures
- File I/O problems

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages in the app
3. Open an issue in the repository

---

**Happy prompting with Claude! 🤖✨**