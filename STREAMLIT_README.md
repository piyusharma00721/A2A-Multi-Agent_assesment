# 🌐 Streamlit Web UI for Multi-Agent Query Router

A beautiful, interactive web interface for the Multi-Agent Query Router system built with Streamlit.

## 🚀 Quick Start

### Option 1: Using the Launcher Scripts

**Windows:**
```cmd
run_streamlit.bat
```

**Linux/Mac:**
```bash
./run_streamlit.sh
```

**Python:**
```bash
python run_streamlit.py
```

### Option 2: Direct Streamlit Command

```bash
# Install Streamlit if not already installed
pip install streamlit plotly

# Run the app
streamlit run streamlit_app.py
```

## 🎯 Features

### 💬 Interactive Chat Interface
- **Real-time Chat**: Ask questions and get intelligent responses
- **File Context**: Upload files and ask questions about them
- **Response Details**: View confidence scores, citations, and processing metrics
- **Chat History**: Persistent conversation history during session

### 📁 File Upload & Analysis
- **Multi-format Support**: PDF, TXT, CSV, Excel, Images (PNG, JPG, etc.)
- **Drag & Drop**: Easy file upload interface
- **Batch Processing**: Upload multiple files at once
- **Real-time Analysis**: Instant file processing and analysis
- **OCR Support**: Automatic text extraction from images

### 📊 Analytics Dashboard
- **System Metrics**: Request counts, success rates, processing times
- **Agent Usage**: Visual distribution of agent usage
- **File Type Analytics**: Statistics on processed file types
- **Recent Activity**: Timeline of recent requests and responses

### 🔧 System Status
- **Configuration Validation**: Real-time system health checks
- **API Key Status**: Environment variable validation
- **Performance Metrics**: Live system performance indicators
- **Error Tracking**: Comprehensive error logging and display

## 🎨 UI Components

### Main Interface
- **Header**: Beautiful gradient title with system description
- **Sidebar**: System status, metrics, and agent usage statistics
- **Tabs**: Organized interface with Chat, File Upload, Analytics, and About sections

### Chat Interface
- **Message History**: Persistent chat with user and assistant messages
- **Response Metadata**: Expandable details showing confidence, citations, and processing info
- **File Context**: Automatic file integration when files are uploaded
- **Real-time Processing**: Live status updates during query processing

### File Upload
- **Multi-file Support**: Upload multiple files simultaneously
- **File Information**: Display file names, sizes, and types
- **Analysis Options**: Direct file analysis with detailed results
- **Processing Status**: Real-time feedback on file processing

### Analytics
- **Key Metrics**: Total requests, success rate, processing time, error rate
- **Visual Charts**: Pie charts for agent usage, bar charts for file types
- **Recent Requests**: Expandable list of recent system activity
- **Performance Trends**: Historical performance data

## 🔧 Configuration

### Environment Setup
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Set environment variables
export GOOGLE_API_KEY=your_api_key_here
```

### Customization
The UI can be customized by modifying:
- **Colors**: Update CSS in `streamlit_app.py`
- **Layout**: Modify column configurations and tab structure
- **Metrics**: Add new metrics in the analytics section
- **Styling**: Customize the agent cards and status indicators

## 📱 Responsive Design

The interface is fully responsive and works on:
- **Desktop**: Full-featured experience with all components
- **Tablet**: Optimized layout for medium screens
- **Mobile**: Simplified interface for small screens

## 🚀 Performance Features

### Caching
- **Orchestrator Caching**: System components cached for faster startup
- **Session State**: Chat history and file uploads persist during session
- **Efficient Updates**: Only necessary components re-render

### Real-time Updates
- **Live Metrics**: System statistics update in real-time
- **Processing Status**: Real-time feedback during query processing
- **Error Handling**: Immediate error display and recovery

## 🔒 Security Features

### File Handling
- **Temporary Storage**: Files stored in secure temporary directories
- **Type Validation**: Strict file type checking
- **Size Limits**: Configurable file size restrictions
- **Cleanup**: Automatic cleanup of temporary files

### API Security
- **Environment Variables**: Secure API key storage
- **Error Masking**: Sensitive information not exposed in errors
- **Input Validation**: Comprehensive input sanitization

## 📊 Monitoring & Analytics

### System Metrics
- **Request Tracking**: Complete request/response logging
- **Performance Monitoring**: Processing time and success rate tracking
- **Agent Usage**: Detailed agent selection and usage statistics
- **Error Analysis**: Comprehensive error tracking and categorization

### Visual Analytics
- **Interactive Charts**: Plotly-powered visualizations
- **Real-time Updates**: Live metric updates
- **Export Options**: Data export capabilities
- **Historical Trends**: Performance trend analysis

## 🛠️ Troubleshooting

### Common Issues

**1. Streamlit Not Starting**
```bash
# Check if Streamlit is installed
pip install streamlit

# Check Python version
python --version
```

**2. API Key Issues**
```bash
# Check environment variable
echo $GOOGLE_API_KEY

# Create .env file
echo "GOOGLE_API_KEY=your_key" > .env
```

**3. File Upload Problems**
- Check file size limits
- Verify supported file types
- Ensure sufficient disk space

**4. Performance Issues**
- Check system resources
- Monitor processing times
- Review error logs

### Debug Mode
```bash
# Run with debug information
streamlit run streamlit_app.py --logger.level debug
```

## 🔄 Updates & Maintenance

### Regular Updates
- **Dependencies**: Keep Streamlit and other packages updated
- **Configuration**: Review and update system settings
- **Logs**: Monitor and clean up log files
- **Performance**: Regular performance optimization

### Backup & Recovery
- **Configuration**: Backup .env and config files
- **Logs**: Regular log file backups
- **Data**: Export important analytics data

## 📈 Future Enhancements

### Planned Features
- **User Authentication**: Multi-user support with login system
- **Advanced Analytics**: More detailed performance metrics
- **Export Options**: Data export in multiple formats
- **API Integration**: REST API for external integrations
- **Mobile App**: Native mobile application
- **Real-time Collaboration**: Multi-user chat sessions

### Customization Options
- **Themes**: Multiple UI themes and color schemes
- **Layouts**: Customizable interface layouts
- **Widgets**: Additional interactive components
- **Integrations**: Third-party service integrations

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review system logs
3. Verify configuration settings
4. Test with sample queries and files

## 🎉 Getting Started

1. **Install Dependencies**: `pip install streamlit plotly`
2. **Set API Key**: Create `.env` file with `GOOGLE_API_KEY`
3. **Run the App**: Use launcher scripts or direct Streamlit command
4. **Open Browser**: Navigate to `http://localhost:8501`
5. **Start Chatting**: Upload files and ask questions!

---

**Enjoy using the Multi-Agent Query Router with its beautiful Streamlit interface! 🚀**
